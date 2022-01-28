import os
import sys
from optparse import OptionParser

sys.path.insert(0, os.path.join(sys.path[0], ".."))
from tiknib.idascript import IDAScript
from tiknib.utils import do_multiprocess
from config.path_variables import IDA_PATH, IDA_FETCH_FUNCDATA

if __name__ == "__main__":
    op = OptionParser()
    op.add_option(
        "--indir", action="store", type=str, dest="indir", help="Input directory"
    )
    op.add_option(
        "--idapath",
        action="store",
        type=str,
        dest="idapath",
        default=IDA_PATH,
        help="IDA directory path",
    )
    op.add_option(
        "--idc",
        action="store",
        type=str,
        dest="idc",
        default=IDA_FETCH_FUNCDATA,
        help="IDA script file",
    )
    op.add_option(
        "--idcargs",
        action="store",
        type=str,
        dest="idcargs",
        default="",
        help="arguments seperated by ',' (e.g. --idcargs a,b,c,d)",
    )
    op.add_option("--force", action="store_true", dest="force")
    op.add_option("--log", action="store_true", dest="log")
    op.add_option("--stdout", action="store_true", dest="stdout")
    op.add_option("--debug", action="store_true", dest="debug")
    op.add_option(
        "--input_list",
        action="store",
        type=str,
        dest="input_list",
        help="A file containing paths of target binaries",
    )

    (opts, args) = op.parse_args()
    assert opts.input_list and os.path.exists(opts.input_list)

    idascript = IDAScript(
        idapath=opts.idapath,
        idc=opts.idc,
        idcargs=opts.idcargs,
        force=opts.force,
        log=opts.log,
        stdout=opts.stdout,
        debug=opts.debug,
    )
    idascript.run(opts.input_list)
