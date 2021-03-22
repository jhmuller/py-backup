#!/usr/bin/env python

import os
import sys
import datetime
import time
import inspect
import warnings
import traceback
import hashlib
import zlib
import zipfile
import pickle
import shutil
import re
import logging
import pandas as pd
from pathlib import PurePath
from collections import OrderedDict
from collections import namedtuple
import subprocess
from subprocess import Popen, PIPE
print("python exe: {0}".format(sys.executable))
# import win32api


__version__ = "0.1.1"


# Force logger.warning() to omit the source code line in the message
# formatwarning_orig = warnings.formatwarning
# warnings.formatwarning = lambda message, category, filename, lineno, line=None: \
#    formatwarning_orig(message, category, filename, lineno, line='')

class Utilities(object):
    def __init__(self):
        pass

    colors_txt = OrderedDict()
    colors_txt['black'] = "\033[90m"
    colors_txt['red'] = "\033[91m"
    colors_txt["green"] = "\033[92m"
    colors_txt["yellow"] = "\033[93m"
    colors_txt["blue"] = "\033[94m"
    colors_txt["gray"] = "\033[97m"
    
    colors_bg = OrderedDict()
    colors_bg['black'] = "\033[100m"
    colors_bg["red"] = "\033[101m"
    colors_bg["green"] = "\033[102m"
    colors_bg["yellow"] = "\033[103m"
    colors_bg["blue"] = "\033[104m"
    colors_bg["gray"] = "\033[107m"
    colors_bg["none"] = "\033[107m"

    txt_effects = OrderedDict()
    txt_effects["end"] = "\033[0m"
    txt_effects["bold"] = "\033[1m"
    txt_effects["underline"] = "\033[4m"
    txt_effects["blackback"] = "\033[7m"

    @staticmethod
    def username():
        return username

    @staticmethod
    def os_whoami():
        proc = subprocess.Popen(['whoami'], stdout=subprocess.PIPE)
        out, errs = proc.communicate()
        return (out)

    @staticmethod
    def now():
        return datetime.datetime.now()

    @staticmethod
    def nowshortstr(fmt="%Y%m%d_%H%M%S"):
        now = datetime.datetime.now()
        res = now.strftime(fmt) + "_" + str(now.microsecond %  10000)
        return res


    @staticmethod
    def nowstr(fmt="%Y-%m-%d__%H_%M_%S"):
        return datetime.datetime.now().strftime(fmt)

    @staticmethod
    def color_str(s, txt_color='black', bg_color=None,
                  bold=False, underline=False,
                  verbosity=0):
        '''
        embedd hex codes for color or effects

        Parameters
        ----------
        s: srting to be enhanced
        txt_color: color for text.  e.g. black, red, green, blue
        bg_color: background color
        bold: boolean
        underline: boolean
        verbosity: level of diagnostics

        Returns
        -------
        string with original and enhancements at the start
        '''
        if verbosity > 0:
            print("{0} <{1}>".format(Utilities.whoami(), Utilities.now()))
        if not isinstance(s, str):
            msg0 = "input s must be string, got {0}".format(type(s))
            msg0 += "trying to convert to string"
            msg = Utilities.color_str(msg0, txt_color="red")
            print(msg)
        try:
            s = str(s)
        except Exception as e:
            msg2 = Utilities.color_str(str(e), txt_color="red", bg_color="red")
            print(msg2)
            raise RuntimeError(msg2)
        result = ''
        if txt_color:
            txt_color = txt_color.lower()
            if txt_color not in Utilities.colors_txt.keys():
                warnings.warn("txt_color '{0}' not a valid color".format(txt_color))
                txt_color = 'black'
        else:
            txt_color = 'black'
        result += Utilities.colors_txt[txt_color]
        if bg_color:
            bg_color = bg_color.lower()
            if bg_color not in Utilities.colors_bg.keys():
                warnings.warn("bg_color '{0}' not a valid color".format(txt_color))
                bg_color = 'none'
        else:
            bg_color = 'none'
        result += Utilities.colors_bg[bg_color]
        if bold:
            result += Utilities.txt_effects['bold']
        if underline:
            result += Utilities.txt_effects['underline']
        result += s + Utilities.txt_effects['end']
        return result

    @staticmethod
    def last_exception_parts():
        (extype, exval, tb) = sys.exc_info()
        return extype, exval, tb

    @staticmethod
    def last_exception_info(verbose=0):
        '''
        returns a string with info about the last exception
        :param verbose:
        :return: string with info about the last exception
        '''
        if verbose > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        msg = "Exception {0}".format(datetime.datetime.now())
        (extype, exval, tb) = sys.exc_info()
        msg += "\n {0}  type: {1}".format(str(exval), extype)
        tblist = traceback.extract_tb(tb, limit=None)
        lines = traceback.format_list(tblist)
        for i, line in enumerate(lines):
            msg += "\n[{0}] {1}".format(i, line)
        result = Utilities.color_str(msg, txt_color="red")
        return result
    
    @staticmethod
    def drives(verbosity=0):
        raise RuntimeError("No longer supported")
        fields = ["drive", "dname", "message"]
        DriveTup = namedtuple("DriveTup", fields)
        dlist = []
        drive_strings = None # win32api.GetLogicalDriveStrings()
        drives = drive_strings.split('\000')[:-1]
        for drive in drives:
            dname = None
            msg = ''
            try:
                dname = None # win32api.GetVolumeInformation(drive)[0]
            except Exception as e:
                msg = str(e)
            dt = DriveTup(drive, dname, msg)
            dlist.append(dt)
        df = pd.DataFrame(dlist)
        df.columns = fields
        return df

    @staticmethod
    def module_versions(verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        mlist = list(filter(lambda x: inspect.ismodule(x[1]), globals().items()))
        if verbosity > 0:
            print(mlist)
        fields = ["filename", "asname", "ver"]
        ModTup = namedtuple("ModTup", fields)
        tlist = []
        for asname, mod in mlist:
            fname = asname
            ver = None
            if asname.startswith("__"):
                continue
            if hasattr(mod, "__version__"):
                fname = asname
                if hasattr(mod, "__path__"):
                    fname = os.path.split(mod.__path__[0])[1]
                ver = mod.__version__
            mt = ModTup(fname, asname, ver)
            tlist.append(mt)
        df = pd.DataFrame(tlist)
        df.columns = fields
        return df

    @staticmethod
    def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
        return ' %s:%s: %s:%s' % (filename, lineno, category.__name__, message)

    @staticmethod
    def whoami():
        return sys._getframe(1).f_code.co_name

    @staticmethod
    def is_file_binary(filepath,
                       nlines=1000,
                       verbosity=0):
        try:
            with open(filepath, "r") as f:
                for _ in range(nlines):
                    line = f.readline()
                    line.lower()
        except UnicodeDecodeError:
            return True
        return False

    @staticmethod
    def sha_256(fpath,
                fmode='rb',# default is text mode
                encoding=None,
                size=4096):
        logger = logging.getLogger(__file__)
        m = hashlib.sha256()
        try:
            lastchunk = None
            fsize = os.path.getsize(fpath)
            with open(fpath, mode=fmode, encoding=encoding) as fp:
                try:
                    chunk = None
                    while True:
                        lastchunk = chunk
                        chunk = fp.read(size)
                        if chunk is None or chunk == b'':
                            break
                        m.update(chunk)
                except Exception as ex:
                    errmsg = "fpath: {0}".format(fpath)
                    errmsg += Utilities.last_exception_info()
                    logger.warning(errmsg)
                    (extype, exval, tb) = sys.exc_info()
                    raise extype(exval)
            return m.hexdigest()
        except PermissionError as pe:
            errmsg = "fpath: {0}".format(fpath)
            errmsg += Utilities.last_exception_info()
            logger.warning(errmsg)
            # if tried text, then try binary
            if fmode == 'r':
                return Utilities.sha_256(fpath, fmode='rb', encoding=None)
            else:
                raise PermissionError(pe)
        except TypeError as te:
            errmsg = "fpath: {0}".format(fpath)
            errmsg += Utilities.last_exception_info()
            logger.warning(errmsg)
            if fmode == 'r':
                # try binary
                return Utilities.sha_256(fpath, fmode='rb', encoding=None)
            raise TypeError(te)
        except OSError as oe:
            errmsg = "fpath: {0}".format(fpath)
            errmsg += Utilities.last_exception_info()
            logger.warning(errmsg)
            OSError(oe)
        except Exception as e:
            errmsg = "fpath: {0}".format(fpath)
            errmsg += Utilities.last_exception_info()
            logger.warning(errmsg)
            (extype, exval, tb) = sys.exc_info()
            raise extype(exval)

    @staticmethod
    def handle_exc(e, rethrow=False):
        msg = Utilities.last_exception_info()
        print(msg)
        if rethrow:
            raise RuntimeError(e)

    @staticmethod
    def create_new_zip(infilepath, zipfilepath,
                       compression=zipfile.ZIP_DEFLATED,
                       compresslevel=zlib.Z_DEFAULT_COMPRESSION,
                       verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        if verbosity > 1:
            print("creating zipfile {0} from {1} <{2}>".format(infilepath, zipfilepath,
                                                               datetime.datetime.now()))
        zf = zipfile.ZipFile(zipfilepath, mode='w', compression=compression,
                             compresslevel=compresslevel)
        try:
            if verbosity > 1:
                print("adding {0}".format(infilepath))
            zf.write(infilepath)
        except Exception as e:
            zf.close()
            msg = "infilepath= {0}".format(infilepath)
            msg += Utilities.last_exception_info()
            print(msg)
            raise RuntimeError(msg)
        finally:
            if verbosity > 1:
                print('Done, closing <{0}>'.format(datetime.datetime.now()))
            zf.close()
        return zf

    @staticmethod
    def path2string(fpath, sep="_", verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        pathstring = ""
        pathleft = fpath
        while True:
            pathleft, tail = os.path.split(pathleft)
            if len(tail) == 0:
                break
            pathstring = tail + sep + pathstring
        if verbosity > 0:
            print("pathstring= {0}".format(pathstring))
        return pathstring

    @staticmethod
    def check_outdir(outdir, create=True, verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        if os.path.isdir(outdir):
            return outdir

        warnings.warn("{0} not a dir".format(outdir))
        if not create:
            return None

        if verbosity > 0:
            print("trying to create {0}".format(outdir))
        os.makedirs(outdir)
        if not os.path.isdir(outdir):
            raise RuntimeError("Cannot make dir= '{0}'".format(outdir))
        return outdir

    @staticmethod
    def make_metafilepath(outdir, basename="generic",
                          sep="_", ext="",
                          verbosity=0):
        # Figure out the filename this code should used based on
        # what files already exist.
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        while True:
            outfilename = basename + sep + Utilities.nowshortstr() + ext
            if not os.path.exists(outfilename):
                break
        if verbosity > 0:
            print("Creating '{0}'".format(outfilename))

        outfilepath = os.path.join(outdir, outfilename)
        return outfilepath

    @staticmethod
    def make_tempfilepath(folder, base, sep="_", ext="",
                          max_attempts=3,
                          exist_ok=True,
                          verbosity=0):
        if verbosity > 1:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
            print("folder len {0}, folner name: {1}".format(len(folder), folder))
        filepath = None
        if not os.path.isdir(folder):
            if verbosity > 0:
                print("trying to make folder {0}".format(folder))
            try:
                os.makedirs(folder, exist_ok=exist_ok)
            except FileNotFoundError as fe:
                msg = Utilities.last_exception_info()
                warnings.warn(msg)
                raise FileNotFoundError(fe)
            except Exception as e:
                msg = Utilities.last_exception_info()
                warnings.warn(msg)
                raise RuntimeError(e)
        attempt = 0
        while attempt < max_attempts:
            filename = base + sep + Utilities.nowshortstr() + ext
            filepath = os.path.join(folder, filename)
            if len(filepath) > 250:
                logger = logging.getLogger(__file__)
                msg = "filepath len= {0}".len(filepath)
                msg += "\n base= {0}".format(base)
                base = re.sub(" ","",base)
                msg += "newbase= {0}".format(base)
                logger.warning(msg)
                continue
            if not os.path.exists(filepath):
                break
            attempt += 1
        return filepath

    @staticmethod
    def import_backup_metafile(folder, filename, verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            raise ValueError("Cannot find file {0} in folder {1}".format(filename, folder))
        data = []
        with open(filepath, "rb") as fp:
            while True:
                try:
                    x = pickle.load(fp)
                    data.append(x)
                except EOFError:
                    # this is expected
                    break
                except Exception as e:
                    Utilities.handle_exc(e)
        return data

    @staticmethod
    def check_folder_filename(folder, filename, verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            raise ValueError("Cannot find file {0} in folder {1}".format(filename, folder))
        meta = Utilities.import_backup_metafile(folder=folder, filename=filename)
        if len(meta) == 0:
            warnings.warn("Empty metafile {0} in {1}".format(filename, folder))
            return False
        return True

    @staticmethod
    def get_meta(folder, filename, verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        if not Utilities.check_folder_filename(folder, filename):
            return False

        meta = Utilities.import_backup_metafile(folder=folder, filename=filename)
        if len(meta) == 0:
            warnings.warn("Empty metafile {0} in {1}".format(filename, folder))
            return None

        if not meta[0]['rec_type'] == "meta_info":
            msg = "file= {0}, folder= {1}\n first elem is not meta {2}".format(filename, folder, meta[0])
            warnings.warn(msg)
            return None
        return meta

    @staticmethod
    def get_meta_fields(folder, filename):
        if not Utilities.check_folder_filename(folder, filename):
            return False

        meta = Utilities.get_meta(folder, filename)
        if not meta:
            return None

        res = {"meta_info": list(meta[0].keys())}
        if len(meta) > 1:
            res["file_info"] = list(meta[1].keys())
        return res

    @staticmethod
    def get_meta_info(folder, filename, meta_fields=None,
                      file_info_fields=None, verbosity=0):
        if not Utilities.check_folder_filename(folder, filename):
            return False

        meta = Utilities.get_meta(folder, filename)
        if not meta:
            return None
        result = ""
        act_fields = Utilities.get_meta_fields(folder, filename)
        fields = []
        if meta_fields:
            for f in meta_fields:
                if f in act_fields['meta_info']:
                    fields.append(f)
                else:
                    warnings.warn(" requested meta_field {0} not in meta_fields".format(f))
        else:
            fields = act_fields['meta_info']

        msglst = ["{0}: {1}".format(f, meta[0][f]) for f in fields]
        result += ", ".join(msglst)
        result += "\n"

        nfiles = sum([int(e['rec_type']=='file_info') for e in meta])
        result += "{0} files".format(nfiles)
        result += "\n"

        fields = []
        if file_info_fields:
            for f in file_info_fields:
                if f in act_fields['file_info']:
                    fields.append(f)
                else:
                    warnings.warn(" requested file_info_field {0} not in file_info_fields".format(f))
        else:
            fields = act_fields['file_info']

        for i, elem in enumerate(meta[1:]):
            msglst = ["[{0}]: {1}: {2}".format(i, f, elem[f]) for f in fields]
            result += ", ".join(msglst)
            result += "\n"
        return result

    @staticmethod
    def check_make_path(thepath, verbosity=0):
        if os.path.isdir(thepath):
          return thepath

        warnings.warn("{0} not a dir".format(thepath))

        if verbosity > 0:
          print("trying to create {0}".format(thepath))

        os.makedirs(thepath)
        if not os.path.isdir(thepath):
            raise RuntimeError("Cannot make dir= '{0}'".format(thepath))

        return thepath

    @staticmethod
    def is_iterable(obj):
        try:
            obj = iter(obj)
            return True
        except:
            return False

    @staticmethod
    def check_folders(folders):
        if isinstance(folders, str):
            folders = [folders]
        elif not Utilities.is_iterable(folders):
            msg = "folders is type {0}, not iterable".format(type(folders))
            raise ValueError(msg)
        errmsg = ''
        for folder in folders:
            if not os.path.isdir(folder):
                errmsg += "'{0}' is not a dir".format(folder)
        if len(errmsg) > 0:
            raise ValueError(errmsg)
        return True

    @staticmethod
    def unzip_to_temp(zipfilepath,
                      tempfolder=None,
                      tempname="temp",
                      verbosity=0):
        if verbosity > 0:
            ldict = locals()
            msg = "{0} <{1}>".format(Utilities.whoami(), Utilities.now())
            for key in ldict.keys():
                print("{0}: {1}".format(key, ldict[key]))

        if tempfolder is None:
            tempfolder = os.path.split(zipfilepath)[0]
        zfile = zipfile.ZipFile(zipfilepath, mode='r')
        zpath = os.path.split(zipfilepath)[0]
        while True:
            tempname = tempname + Utilities.nowshortstr()
            temppath = os.path.join(zpath, tempname)
            if not os.path.isfile(temppath):
                break
            else:
                msg = "Found temp file {0} in {1}\n try another".format(tempname, zpath)
        zinfolist = zfile.infolist()
        if len(zinfolist) != 1:
            zlen = len(zinfolist)
            msg = "file = {0}, zinfolist len= {1}, should be 1".format(zipfilepath, zlen)
            raise ValueError(msg)
        zinfo = zinfolist[0]
        zipname = zinfo.filename
        try:
            if verbosity > 0:
                print("zipname= {0} ".format(zipname))
            zfile.extract(member=zipname,
                          path=temppath, pwd=None)
        except Exception as e:
            Utilities.last_exception_info()
            raise Exception(e)
        finally:
            zfile.close()
        return temppath


class GitBack(object):
    def __init__(self,
                 logfilepath=None,
                 loglevel=logging.DEBUG,
                 dt_fmt="%Y%m%d_%H%M%S",
                 verbosity=0):
        self.verbosity = verbosity
        self.dt_fmt = dt_fmt
        if logfilepath is None:
            logfilepath = __name__ + "_" + Utilities.nowstr(fmt=self.dt_fmt) + ".log"
        logger = logging.getLogger(__file__)
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)
        logging.basicConfig(filename=logfilepath, level=loglevel)

    def backup_folders(self, folders=None,
                       dest_drive=None,
                       dest_folder=None,
                       temp_folder=None,
                       exclude_folders=None,
                       include_exts=None,
                       exclude_exts=None,
                       verbosity=0):
        """
        try to backup folders to a destination

        :param folders: list of folders to backup
        :param dest_drive: destination drive
        :param dest_folder: destination root directory
        :param temp_folder: for temp files
        :param exclude_folders: folder names to exclude
        :param include_exts: extensions to include
        :param exclude_exts: extensions to exclude
        :param verbosity: level of diagnostics
        :return: 0 on success
        """

        ldict = locals()
        verbosity = max(self.verbosity, verbosity)
        logger = logging.getLogger(__file__)
        Utilities.check_folders(folders)
        errmsg = ''
        req_param_types = {"folders": list,
                           "dest_drive": str,
                           "dest_folder": str}
        for pname in req_param_types.keys():
            ptype = req_param_types[pname]
            val = ldict[pname]
            if val is None:
                errmsg += "No {0} specified".format(pname)
            elif not isinstance(val, ptype):
                errmsg += "{0} should be {1}, got {2}".format(pname, ptype, type(val))
        if len(errmsg) > 0:
            raise RuntimeError(errmsg)

        msg = "Backup starting {0}".format(datetime.datetime.now())
        logger.info(msg)
        
        for folder in folders:
            if not os.path.isdir(folder):
                msg = "'{0}' not a folder".format(folder)
                raise ValueError(msg)
            pp = PurePath(folder)
            less_drive = os.sep.join(pp.parts[1:])
            # descr_root = os.path.join(dest_drive, dest_root)
            destroot = os.path.join(dest_drive, dest_folder)
            msg = "Source folder= {0}".format(folder)
            msg += "\nSource less drive: {0}".format(less_drive)
            msg += "\nDest root: {0}".format(destroot)
            logger.info(msg)
            try:
                if verbosity > 0:
                    items = os.listdir(folder)
                    n = min(len(items), 7)
                    logger.info("Found {0}".format(items[:n]))
                self.backup_folder(sourceroot=folder,
                                   destroot=destroot,
                                   exclude_exts=exclude_exts,
                                   exclude_folders=exclude_folders,
                                   tempfolder=temp_folder,
                                   testing=False,
                                   verbosity=verbosity)
            except PermissionError as e:
                msg = Utilities.last_exception_info(verbose=verbosity)
                warnings.warn(msg)
                raise PermissionError(msg)
            except Exception as e:
                msg = Utilities.last_exception_info(verbose=verbosity)
                logger.error(msg)
                warnings.warn(e)
                raise RuntimeError(msg)
            else:
                msg = "Seems ok {0}".format(datetime.datetime.now())
                logger.info(msg)
        return 0

    def backup_folder(self, sourceroot,
                      destroot,
                      tempfolder=None,
                      exclude_folders=None,
                      include_exts=None,
                      exclude_exts=None,
                      dt_fmt='%Y-%m-%dT%H:%M:%S',
                      comp_thresh=0.9,
                      compression=zipfile.ZIP_DEFLATED,
                      compresslevel=zlib.Z_DEFAULT_COMPRESSION,
                      testing=False,
                      verbosity=0):

        """
        try to make a backup of a single folder
        :param sourceroot: original (source) path
        :param destroot: destination path
        :param tempfolder: folder for temp files
        :param include_exts: file extensions to include
        :param exclude_exts: file extensions to exclude
        :param dt_fmt: format for dates
        :param comp_thresh: threshold for compression
            if compression ratio less than this then don't compress
        :param compression: method for compression
        :param compresslevel: level of compression
        :param testing: switch for just testing process
        :param verbosity: level of diagnostics
        :return: 0 on success
        """
        argdict = locals().copy()
        verbosity = max(verbosity, self.verbosity)
        logger = logging.getLogger(__file__)
        if verbosity > 0:
            msg = "{0} <{1}>".format(Utilities.whoami(), Utilities.now())
            for key in argdict.keys():
                msg += "\n  {0}: {1}".format(key, argdict[key])
            logger.info(msg)
        try:
            if tempfolder is None:
                tempfoldername = "zztemp"
                tempfolder = os.path.join(os.path.splitext(__file__)[0], tempfoldername)
                if exclude_folders is None:
                    exclude_folders = []
                exclude_folders.append(tempfoldername)

            if os.path.isdir(tempfolder):
                tempfiles = os.listdir(tempfolder)
                for tfile in tempfiles:
                    os.remove(os.path.join(tempfolder, tfile))

            if not os.path.isdir(tempfolder):
                os.mkdir(tempfolder)

            if verbosity > 0:
                logger.info("  tempfolder= {0}".format(tempfolder))
        except Exception as e:
            msg = Utilities.last_exception_info()
            logger.warning(msg)
            RuntimeError(e)


        # process include_exts and exclude_exts
        for xname in ('include_exts', 'exclude_exts'):
            x = argdict[xname]
            if isinstance(x, str):
                x = [x]
            if isinstance(x, list):
                if len(x) == 0:
                    x = None
            elif x is not None:
                raise ValueError("{0} should be None or string or list of strings")
            if verbosity > 1:
                logger.info("{0}: {1}".format(xname, x))
            locals()[xname] = x

        pp_sourceroot = PurePath(sourceroot)
        if not pp_sourceroot.is_absolute():
            logger.warning("sourceroot must be absolute, {0}".format(sourceroot))

        pp_destroot = PurePath(destroot)
        if not pp_destroot.is_absolute():
            logger.warning("destroot must be absolute, {0}".format(destroot))

        if (sourceroot == destroot) or (pp_sourceroot == pp_destroot):
            msg = "sourceroot cannot be same as destfolder"
            msg += "Please choose a different destfolder so files will not be overwritten"
            raise RuntimeError(msg)

        Utilities.check_make_path(destroot, verbosity=verbosity)

        destfolder = os.sep.join(pp_destroot.parts[1:])

        # Walk the entire folder tree and compress the files in each folder.

        for dirpath, _, filenames in os.walk(sourceroot, topdown=True):
            pp_dirpath = PurePath(dirpath)
            # dirdrive = pp_dirpath.drive
            dirfolder = os.sep.join(pp_dirpath.parts[1:])
            skip_folder = False
            for ef in exclude_folders:
                if ef in pp_dirpath.parts:
                    skip_folder = True
                    break
            if skip_folder:
                msg = "skipping {0} due to exclude_folder: {1}".format(dirpath,
                                                                       exclude_folders)
                logger.info(msg)
                continue

            if verbosity > 0:
                logger.info("  Adding files from '{0}' to '{1}'".format(dirpath, destfolder))

            for filename in filenames:
                try:
                    if verbosity > 1:
                        msg = "filename: {0}, dirpath: {1}".format(filename, dirpath)
                        logger.info(msg)
                    file_base, file_ext = os.path.splitext(filename)
                    if include_exts is not None:
                        if file_ext not in include_exts:
                            if verbosity > 1:
                                logger.info("  Skipping {0}, {1} not in include_exts".format(filename, file_ext))
                            continue
                    if exclude_exts is not None:
                        if file_ext in exclude_exts:
                            if verbosity > 1:
                                logger.info("  Skipping {0}, {1}  in include_exts".format(filename, file_ext))
                            continue

                    # get the sha256 for the source file
                    sourcepath = os.path.join(dirpath, filename)
                    source_sha256 = Utilities.sha_256(sourcepath, fmode='rb', encoding=None,
                                                      size=4096)

                    # Note: source path becomes a dest folder,
                    #  copies of source files are stored under there
                    temp_dest_folder = os.path.join(destroot, dirfolder)
                    # the backup file will go into the folder/dir this_outpath
                    this_dest_folder = os.path.join(temp_dest_folder, filename)

                    if len(this_dest_folder) > 240:
                        logger.warning("  Potential problem, path length = {0}".format(len(this_dest_folder)))
                        # try removing spaces from the filename
                        shortfilename = res.sub(" ", "", filename)
                        this_dest_folder = os.path.join(temp_dest_folder, filename)
                        if len(this_dest_folder) > 256:
                            msg = "dest path len= {0} too long".format(len(this_dest_folder))
                            msg += "\n   {0}".format(this_dest_folder)
                            logger.error(msg)
                            continue
                    # now check and see if the dest folder exists
                    found_sha_match = False
                    if os.path.isdir(this_dest_folder):
                        # if there is a folder there
                        #  check all the files int the folder
                        #  to see if one of the fils sha_256 matches the source's
                        #  if so, contents the same and no need to backup
                        # NOTE: should I just check the lastest file?
                        dest_files = os.listdir(this_dest_folder)
                        for dfile in dest_files:
                            dpath = os.path.join(this_dest_folder, dfile)
                            if not os.path.isfile(dpath):
                                continue
                            dext = os.path.splitext(dfile)[1]
                            if dext == "zip":
                                # have to unzip to check
                                temppath = Utilities.unzip_to_temp(dpath,
                                                                   tempfolder=tempfolder)
                                dest_sha256 = Utilities.sha_256(temppath, size=4096)
                            else:
                                dest_sha256 = Utilities.sha_256(dpath, size=4096)
                            if source_sha256 == dest_sha256:
                                found_sha_match = True
                                break
                except OSError as oe:
                    msg = Utilities.last_exception_info()
                    logger.warning(msg)
                    OSError(oe)
                except Exception as e:
                    msg = Utilities.last_exception_info()
                    logger.warning(msg)
                    RuntimeError(e)

                try:
                    if found_sha_match:
                        # then the same contents are already there
                        if verbosity > 1:
                            msg = "no need to backup {0}, {1} there with same contents".format(filename, dfile)
                            logger.info(msg)
                        continue
                    # at this point we need to backup
                    if verbosity > 0:
                        logger.info("  backing up {0} from {1} to {2}".format(filename, dirpath,
                                                                        this_dest_folder))
                    if testing:
                        # if testing nothing more to do
                        continue

                    # try to zip the file
                    def zipit(sourcepath,
                              tempfolder,
                              verbosity=0):
                        zipfilepath = Utilities.make_tempfilepath(tempfolder,
                                                                  base="temp",
                                                                  ext=".zip",
                                                                  verbosity=verbosity)
                        tries = 0
                        ok = False
                        while tries < 10 and not ok:
                            try:
                                tries += 1
                                time.sleep(0.01)
                                zf = Utilities.create_new_zip(sourcepath, zipfilepath)
                                #zfile = zipfile.ZipFile(zipfilepath, mode='r')
                            except OSError as oe:
                                msg = "\nsourcepath: {0}\nzipfilepath: {1}".format(sourcepath,
                                                                                 zipfilepath)
                                msg += Utilities.last_exception_info()
                                print(msg)
                            except Exception as e:
                                msg = "\nsourcepath: {0}\nzipfilepath: {1}".format(sourcepath,
                                                                                   zipfilepath)
                                msg += Utilities.last_exception_info()
                                print(msg)
                            else:
                                ok = True
                        if not ok:
                            msg = "can't create zfile {0} ".format(zipfilepath)
                            raise RuntimeError(msg)
                        return zipfilepath, zf.filelist[0].filename
                    zipfilepath, zfilename = zipit(sourcepath, tempfolder, verbosity=verbosity)
                    orig_size = os.path.getsize(sourcepath)
                    comp_size = os.path.getsize(zipfilepath)
                    comp_ratio = 1
                    if orig_size == 0:
                        logger.warning("{0} in {1} size is {2}".format(filename, dirpath, orig_size))
                    else:
                        comp_ratio = float(comp_size)/orig_size

                    # if compression ratio not less then thresh
                    #  just use original file
                    compressed = True
                    if comp_ratio > comp_thresh:
                        compressed = False
                        infilepath = sourcepath
                    else:
                        infilepath = zipfilepath

                    # this_outfilebase = os.path.splitext(ddict['filename'])[0]
                    # this_outfilename = filename

                    this_ext = file_ext
                    if compressed:
                        this_ext = ".zip"

                    # construct the dest file path
                    dest_file_path = Utilities.make_tempfilepath(this_dest_folder,
                                                                 base=file_base,
                                                                 ext=this_ext,
                                                                 verbosity=verbosity)
                except OSError as oe:
                    msg = Utilities.last_exception_info()
                    logger.info(msg)
                    OSError(oe)
                except Exception as e:
                    msg = Utilities.last_exception_info()
                    logger.info(msg)
                    RuntimeError(e)
                    # copy source to destination
                try:
                    dfolder = os.path.split(dest_file_path)[0]
                    if not os.path.isdir(dfolder):
                        msg = " destination folder missing: {0}".format(dfolder)
                        logger.error(msg)
                        raise RuntimeError(msg)
                    tsize =None
                    if not os.path.isfile(infilepath):
                        msg = " source file missing: {0}".format(infilepath)
                        logger.error(msg)
                        raise RuntimeError(msg)
                    else:
                        tsize = os.path.getsize(infilepath)
                    shutil.copy(infilepath, dest_file_path)
                except OSError as oe:
                    errmsg = "\ninfilepath: {0}\n dest_file_path: {1}".format(infilepath,
                                                                            dest_file_path)
                    errmsg += Utilities.last_exception_info()
                    logger.error(errmsg)
                    raise OSError(oe)
                except Exception as exc:
                    errmsg = "infilepath: {0}\n dest_file_path: {1}".format(infilepath,
                                                                            dest_file_path)
                    errmsg += Utilities.last_exception_info()
                    logger.info(errmsg)
                    raise RuntimeError(exc)

                try:
                    # create a dictionary with some file backup info
                    meta_dict = OrderedDict()
                    meta_dict['filename'] = filename
                    meta_dict['folder'] = dirpath
                    meta_dict['filepath'] = sourcepath
                    meta_dict['orig_size'] = orig_size
                    meta_dict['comp_size'] = comp_size
                    meta_dict['sha256'] = source_sha256
                    meta_dict['ctime'] = datetime.datetime.fromtimestamp(os.path.getctime(sourcepath)).\
                        strftime(dt_fmt)
                    meta_dict['mtime'] = datetime.datetime.fromtimestamp(os.path.getmtime(sourcepath)).\
                        strftime(dt_fmt)
                    meta_dict['comp_ratio'] = comp_ratio
                    meta_dict['compressed'] = compressed

                    # construct a path for this meta data
                    meta_folder = os.path.join(this_dest_folder, "meta_files")
                    meta_file_path = Utilities.make_tempfilepath(meta_folder,
                                                                 base="meta",
                                                                 ext=".txt",
                                                                 verbosity=verbosity)
                    # write the meta_dict to a file in dest folder
                    if len(meta_file_path) > 250:
                        logger.info("  problem path len= {0}".format(len(meta_file_path)))
                    with open(meta_file_path, mode="w") as fp:
                        for key in meta_dict.keys():
                            fp.write("{0}: {1}\n".format(key, meta_dict[key]))
                except FileNotFoundError as fnfe:
                    errmsg = Utilities.last_exception_info()
                    logger.info(errmsg)
                    # ignore it for now
                    raise FileNotFoundError(fnfe)
                except OSError as oe:
                    errmsg = Utilities.last_exception_info()
                    logger.info(errmsg)
                    raise OSError(oe)
                except Exception as e:
                    err_msg = Utilities.last_exception_info()
                    logger.warning(err_msg)
                    raise RuntimeError(e)

                try:
                    if verbosity > 0:
                        msg = "filename: {0}, filepath: {1}".format(filename, sourcepath)
                        msg += ", osize= {0}, csize= {1}".format(orig_size, comp_size)
                        msg += ", compressed= {0}".format(compressed)
                        msg += "\n infilepath: {0} dest folder: {1}".format(infilepath, this_dest_folder)
                        # logger.info("sha_256= {0}".format(ddict['sha256']))
                        logger.info(msg)
                    # remove the temporary zipfile
                    if os.path.isfile(zipfilepath):
                        try:
                            # wait until file fully copied
                            source_size = os.path.getsize(infilepath)
                            dest_size = os.path.getsize(dest_file_path)
                            tries = 0
                            while dest_size < source_size:
                                dest_size = os.path.getsize(dest_file_path)
                                tries += 1
                                if tries > 20:
                                    break
                                time.sleep(0.01)
                            if dest_size > source_size:
                                msg = " {0} tries checking on file, dest not written".format(tries)
                                raise RuntimeError(msg)
                            os.remove(zipfilepath)
                        except Exception as e:
                            msg = "\n  Problem removing zipfile: {0}".format(zipfilepath)
                            msg += "\n zfile: {0}".format(zfile)
                            msg += Utilities.last_exception_info()
                            logger.warning(msg)
                            raise RuntimeError(e)
                    else:
                        msg = "can't find zipfile {0}".format(zipfilepath)
                        raise RuntimeError(msg)
                except OSError as oe:
                    errmsg = Utilities.last_exception_info()
                    logger.info(errmsg)
                    raise OSError(oe)
                except Exception as e:
                    err_msg = Utilities.last_exception_info()
                    logger.warning(err_msg)
                    raise RuntimeError(e)
                try:
                    tempfiles = os.listdir(tempfolder)
                    if len(tempfiles) > 0:
                        msg = "{0} files in {1}".format(len(tempfiles),
                                                            tempfolder)
                        warnings.warn(msg)
                except Exception as e:
                    err_msg = Utilities.last_exception_info()
                    logger.warning(err_msg)
                    raise RuntimeError(e)
        if verbosity > 0:
            logger.info("Done")
        # meta_fp.close()
        return 0

    def find_files_in_backup(self,
                             backuproot,
                             filenames,
                             origfolder=None,
                             verbosity=0):
        argdict = locals().copy()
        verbosity = max(verbosity, self.verbosity)
        logger = logging.getLogger(__file__)
        if verbosity > 0:
            msg = "{0} <{1}>".format(Utilities.whoami(), Utilities.now())
            for key in argdict.keys():
                msg += "\n  {0}: {1}".format(key, argdict[key])
            logger.info(msg)
        if filenames is None:
            warnings.warn("filename is None")
            return -1
        if backuproot is None:
            warnings.warn("backuproot is None")
            return -1
        if not os.path.isdir(backuproot):
            warnings.warn("backuproot <{0}> not a dir".format(backuproot))
            return -1

        found_map = OrderedDict()
        for filename in filenames:
            found_list = self.find_file_in_backup(backuproot=backuproot,
                                      target_filename=filename,
                                      verbosity=0)
            found_map[filename] = found_list
        return found_map

    def find_file_in_backup(self,
                            backuproot,
                            target_filename,
                            origfolder = None,
                            verbosity=0):
        argdict = locals().copy()
        verbosity = max(verbosity, self.verbosity)
        logger = logging.getLogger(__file__)
        if verbosity > 0:
            msg = "{0} <{1}>".format(Utilities.whoami(), Utilities.now())
            for key in argdict.keys():
                msg += "\n  {0}: {1}".format(key, argdict[key])
            logger.info(msg)
        if target_filename is None:
            warnings.warn("target_filename is None")
            return -1
        if backuproot is None:
            warnings.warn("backuproot is None")
            return -1
        if not os.path.isdir(backuproot):
            warnings.warn("backuproot <{0}> not a dir".format(backuproot))
            return -1

        pp_backuproot = PurePath(backuproot)
        if not pp_backuproot.is_absolute():
            logger.warning("backuproot must be absolute, {0}".format(backuproot))

        found_list = []
        for dirpath, dirnames, filenames in os.walk(backuproot, topdown=True):
            #pp_dirpath = PurePath(dirpath)
            # dirdrive = pp_dirpath.drive
            #dirfolder = os.sep.join(pp_dirpath.parts[1:])
            for dirname in dirnames:
                dirfolder = os.path.join(dirpath, dirname)
                if dirname == target_filename:
                    files = [f for f in os.listdir(dirfolder) if os.path.isfile(os.path.join(dirfolder,f))]
                    tup = (dirname, files)
                    found_list.append(tup)
        return found_list

    @staticmethod
    def recover(folder,
                filelist,
                outdir,
                verbosity=0):
        logger = logging.getLogger(__file__)
        if not os.path.isdir(folder):
            logger.warning("{0} is not a folder".format(folder))
            return None

        meta = Utilities.get_meta(folder, meta_filename)

        if not meta:
            return None

        if len(meta) == 1:
            logger.warning("No file_info records")
            return None

        # res = Utilities.check_outdir(outdir, create=create_outdir, verbosity=0)

        filemap = {}
        for i, e in enumerate(meta[1:]):
            filemap[e['filename']] = i+1
        for filename in filelist:
            if filename in filemap.keys():
                ei = filemap[filename]
                msg = "Found {0} as entry {1}".format(filename, ei)
                logger.info(msg)
                file_info = meta[ei]
                logger.info(file_info)
                if file_info['compressed']:
                    outfilepath = Utilities.make_tempfilepath(outdir, base="temp", ext=".zip",
                                                              verbosity=verbosity)
                else:
                    outfilepath = os.path.join(outdir, file_info['filename'])
                logger.info("outfilepath= {0}".format(outfilepath))
                outfilepath = os.path.abspath(outfilepath) # make sure folder is absolute
                logger.info("outfilepath= {0}".format(outfilepath))
                infilename = file_info['sha256']
                infilepath = os.path.join(folder, infilename)
                if not os.path.isfile(infilepath):
                    logger.warning("Cannot fine backup file {0} in {1}".format(infilename, folder))
                    continue
                try:
                    if verbosity > 0:
                        logger.info("copying {0} to {1}".format(infilepath, outfilepath))
                        shutil.copy(infilepath, outfilepath)
                except Exception as e:
                    (extype, exval, tb) = sys.exc_info()
                    logger.warning("extype= {0}, exval= {1}\n {2}".format(extype, exval, tb))

                if file_info['compressed']:
                    zipfilepath = outfilepath
                    outfilepath = os.path.join(outdir, file_info['filename'])
                    logger.info("outfilepath {0}".format(outfilepath))
                if verbosity > 0:
                    logger.info("Unzipping {0} to {1}".format(zipfilepath, outfilepath))

                zfile = zipfile.ZipFile(zipfilepath, mode='r')
                for zm in zfile.infolist():
                    logger.info(zm)
                try:
                    zipname = file_info['zipname']
                    logger.info("zipname= {0}  outfilepath= {1}".format(zipname, outfilepath))
                    zfile.extract(member=zipname,
                                  path=outfilepath, pwd=None)
                except Exception as e:
                    (extype, exval, tb) = sys.exc_info()
                    logger.warning("extype= {0}, exval= {1}\n {2}".format(extype, exval, tb))
                    raise Exception(e)
                zfile.close()
                os.remove(zipfilepath)
        else:
            msg = "No entry for {0}".format(filename)
            logger.warning(msg)
        return None


def _get_args_dict(fn, args, kwargs):
    args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    return {**dict(zip(args_names, args)), **kwargs}


def test_func_name():
    frame = inspect.getframeinfo(inspect.currentframe())
    fname = frame.function
    return fname


def get_fname(i=1):
    frame = sys._getframe(i)
    code = frame.f_code
    fname = code.co_name
    return fname


if __name__ == "__main__":
    Utils = Utilities()
    warnings.formatwarning = Utils.warning_on_one_line
    logger = logging.getLogger(__file__)

    # initialize parameters
    # for new lenovo
    computername = str(os.getenv("COMPUTERNAME"))
    if computername is None:
        logger.error("no computer name")
        exit(-1)
        
    username = str(os.getenv("USERNAME"))
    if username is None:
        logger.error("no user name")
        exit(-1)
    
    if computername.upper() == "LENOVO-LEGION":
        bfolders = [
                    os.path.join("C:\\", "Users", username, "OneDrive", "Desktop"),
                    os.path.join("C:\\", "Users", username, "OneDrive", "Documents"),
                    os.path.join("C:\\", "Users", username, "OneDrive", "Pictures"),
                    os.path.join("C:\\", "Users", username, "Downloads"),
                    os.path.join("C:\\", "Users", username, "Videos"),
                    os.path.join("C:\\", "Users", username, "Music"),
                    os.path.join("C:\\", "Users", username, "Documents"),

                    ]
    elif re.search("hp_small", computer_name):
        bfolders = [
            os.path.join("C:\\", "dev"),
            os.path.join("C:\\", "jmuller"),
            os.path.join("C:\\", "Users", username, "Documents"),
            os.path.join("C:\\", "Users", username, "Downloads"),
            os.path.join("C:\\", "Users", username, "dev"),
            os.path.join("C:\\", "Users", username, "enter2"),
            os.path.join("C:\\", "Users", username, "Pictures"),
            os.path.join("C:\\", "Users", username, "Videos"),
            os.path.join("C:\\", "Users", username, "Music"),
        ]
        bfolders = [
            # os.path.join("C:\\", "dev"),
            # os.path.join("C:\\", "Users", username, "OneDrive", "dev"),
            # os.path.join("C:\\", "Users", username, "enter1"),
            # os.path.join("C:\\", "Users", username, "enter2"),
            # os.path.join("C:\\", "Users", username, "OneDrive", "Desktop"),
            # os.path.join("C:\\", "Users", username, "OneDrive", "Documents"),
            # os.path.join("C:\\", "Users", username, "OneDrive", "Pictures"),
            os.path.join("C:\\", "Users", username, "Documents"),
            os.path.join("C:\\", "Users", username, "Downloads"),
            os.path.join("C:\\", "Users", username, "Videos"),
            os.path.join("C:\\", "Users", username, "Music"),
        ]
    dest_drive = "G:\\"

    dest_folder = os.path.join(dest_drive, computername)
    logfilename = "backup_log" + "_" + Utilities.nowshortstr() + ".txt"
    logfilepath = logfilename
    print("dest folder= {0}".format(dest_folder))

    # create instance of class
    GB = GitBack(verbosity=1)

    res = GB.backup_folders(folders=bfolders,
                        dest_drive=dest_drive,
                        dest_folder=dest_folder,
                        exclude_folders=["zztemp"],
                        exclude_exts=['.exe'],
                        temp_folder="./zztemp",
                        verbosity=1)
    backuproot = os.path.join(dest_drive, dest_folder)
    res = GB.find_files_in_backup(backuproot=backuproot,
                                  filenames=['addenv.bat'])
    print(res)

