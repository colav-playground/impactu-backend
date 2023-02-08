# flake8: noqa
from PDBServer.PDBLoader import PDBLoader

loader=PDBLoader(dbname="colav")
loader.load("../Data/RedalycMetadatosArticulos.csv",dbcollection="data_redalyc")