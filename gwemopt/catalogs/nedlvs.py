import subprocess

import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.io.misc.hdf5 import read_table_hdf5, write_table_hdf5
from astropy.table import Table

from gwemopt.catalogs.base_catalog import BaseCatalog

URL = "https://ned.ipac.caltech.edu/NED::LVS/fits/AsPublished/"


class NEDCatalog(BaseCatalog):
    name = "ned"

    def download_catalog(self):
        temp_path = self.get_temp_path()
        print(f"NED catalog not found locally. Downloading to {temp_path}")
        subprocess.run(
            f"wget -O {self.get_temp_path()} {URL}",
            shell=True,
            check=True,
        )

        hdul = fits.open(temp_path)
        df = pd.DataFrame(np.asarray(hdul[1].data), columns=hdul[1].columns.names)
        df = df.replace({np.nan: None})
        df.rename(
            columns={
                "objname": "name",
                "DistMpc": "distmpc",
                "DistMpc_unc": "distmpc_unc",
                "z": "redshift",
                "z_unc": "redshift_error",
                "Mstar": "mstar",
                "m_Ks": "magk",
                "m_FUV": "mag_fuv",
                "m_NUV": "mag_nuv",
                "SFR_W4": "sfr_w4",
            },
            inplace=True,
        )
        df = df[df["redshift"] > 0]
        cat = Table.from_pandas(df)
        write_table_hdf5(cat, str(self.get_catalog_path()), path="df")
        temp_path.unlink()

    def get_temp_path(self):
        return self.get_catalog_path(filetype="fits").with_stem(f"temp_{self.name}")

    def load_catalog(self) -> pd.DataFrame:
        cat = read_table_hdf5(str(self.get_catalog_path()), path="df")
        df = cat.to_pandas()
        return df
