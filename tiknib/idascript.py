import os
import tempfile
import time
import shutil
from pathlib import Path
from subprocess import run, PIPE

from tiknib.utils import system, get_file_type, do_multiprocess

import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO, logger=logger)


class IDAScript:
    def __init__(
        self,
        idapath="/home/dongkwan/.tools/ida-6.95",
        idc=None,
        idcargs="",
        force=False,
        log=False,
        stdout=False,
        debug=False,
    ):
        self.idapath = idapath
        self.idc = idc
        self.idcargs = idcargs
        self.force = force
        self.log = log
        self.stdout = stdout
        self.debug = debug

        # Need to set xterm for IDA Processing.
        self.env = os.environ.copy()
        self.env["TERM"] = "xterm"
        # By setting this, IDA GUI will not be shown, so we can process
        # command line IDA script processing :)
        self.env["TVHEADLESS"] = "1"
        if self.debug:
            coloredlogs.install(level=logging.DEBUG, logger=logger)
            self.force = True
            self.stdout = True

    # Sometimes, IDA dies even the script is not finished yet. So, we need to
    # process it by checking the leftover files.
    def remove_leftovers(self, input_fname):
        exts = [".id0", ".id1", ".nam", ".til", ".id2"]
        # Note that this differs from os.path.basename()
        basename = os.path.splitext(input_fname)[0]
        for ext in exts:
            try:
                os.remove(basename + ext)
            except:
                pass

    def is_done(self, input_fname):
        return os.path.exists(input_fname + ".done")

    def handle_log(self, input_fname, tmp_fname):
        if not os.path.exists(tmp_fname):
            return

        if self.stdout:
            with open(tmp_fname, "rb") as f:
                data = f.read()
            print(data.decode())

        if self.log:
            res_fname = input_fname + ".output"
            shutil.move(tmp_fname, res_fname)
        else:
            os.unlink(tmp_fname)

    def run_helper(self, input_fname):
        if not os.path.exists(input_fname):
            return input_fname, None

        arch = get_file_type(input_fname)
        if arch is None:
            logger.warn("Skip Unknown file type: %s" % input_fname)
            return input_fname, False

        if not self.force and self.is_done(input_fname):
            return input_fname, True

        self.remove_leftovers(input_fname)

        idc_args = [self.idc]
        idc_args.extend(self.idcargs)
        idc_args = " ".join(idc_args)

        if arch.find("_32") != -1:
            ida = self.idapath + "/idal"
        else:
            ida = self.idapath + "/idal64"

        # >= IDA Pro v7.4 use "idat" instead of "idal"
        if not os.path.exists(ida):
            ida = ida.replace('idal', 'idat')

        # Setup command line arguments
        path = [ida, "-A", "-S{}".format(idc_args)]
        if self.log or self.stdout:
            fd, tmp_fname = tempfile.mkstemp()
            os.close(fd)
            # IDA supports logging by '-L'
            path.append("-L{}".format(tmp_fname))
        path.append(input_fname)
        logger.debug(" ".join(path))

        ret = run(path, env=self.env, stdout=PIPE).returncode
        if self.log or self.stdout:
            self.handle_log(input_fname, tmp_fname)
        if ret != 0:
            logger.error("IDA returned {} for {}".format(ret, input_fname))
            return input_fname, False
        else:
            Path(input_fname + ".done").touch()
            return input_fname, True

    def get_elf_files(self, input_path):
        if os.path.isdir(input_path):
            # If a directory is given, we need to search all ELFs. Note that
            # using system command 'find' is much faster then internal Python
            # scripts when processing a large amount of files.
            cmd = "find {0} -type f -executable | grep ELF".format(input_path)
            fnames = system(cmd)
        else:
            with open(input_path, "r") as f:
                fnames = f.read().splitlines()
        return fnames

    def run(self, input_path):
        elfs = self.get_elf_files(input_path)

        logger.info("[+] start extracting {0} files ...".format(len(elfs)))
        t0 = time.time()

        if self.debug:
            # We only fetch the first ELF for debugging.
            elfs = [elfs[0]]

        # IDA's processing time for each binary is significantly different.
        # Thus, it is better to set the chunk size to 1.
        res = do_multiprocess(self.run_helper, elfs, chunk_size=1, threshold=1)
        logger.info("done in: (%0.3fs)" % (time.time() - t0))
        return res
