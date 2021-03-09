#!/usr/bin/env python

# backupToZip.py
# Copies an entire folder and its contents into
# a zip file whose filename increments.
import os
import sys
import datetime
import inspect
import warnings
import traceback
import hashlib
import zlib
import zipfile
import pickle
import shutil
import subprocess
import pandas as pd
import numpy as np
from pathlib import PurePath
from collections import OrderedDict
from collections import namedtuple
import win32api


__version__ = "0.1.1"


# Force warnings.warn() to omit the source code line in the message
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
        return os.getenv("USERNAME")

    @staticmethod
    def os_whoami():
        proc = subprocess.Popen(['whoami'], stdout=subprocess.PIPE)
        out, errs = proc.communicate()
        return (out)

    @staticmethod
    def now():
        return datetime.datetime.now()

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
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        fields = ["drive", "dname", "message"]
        DriveTup = namedtuple("DriveTup", fields)
        dlist = []
        drive_strings = win32api.GetLogicalDriveStrings()
        drives = drive_strings.split('\000')[:-1]
        for drive in drives:
            dname = None
            msg = ''
            try:
                dname = win32api.GetVolumeInformation(drive)[0]
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
        m = hashlib.sha256()
        try:
            chunk = None
            fsize = os.path.getsize(fpath)
            with open(fpath, mode=fmode, encoding=encoding) as fp:
                for chunk in iter(lambda: fp.read(size), b''):
                    m.update(chunk)
            return m.hexdigest()
        except PermissionError as pe:
            errmsg = Utilities.last_exception_info()
            warnings.warn(errmsg)
            # if tried text, then try binary
            if fmode == 'r':
                return Utilities.sha_256(fpath, fmode='rb', encoding=None)
            else:
                raise PermissionError(pe)
        except TypeError as te:
            errmsg = Utilities.last_exception_info()
            warnings.warn(errmsg)
            if fmode == 'r' and encoding == None:
                return Utilities.sha_256(fpath, fmode='rb', encoding=None)
        except OSError as oe:
            errmsg = Utilities.last_exception_info()
            warnings.warn(errmsg)
            OSError(oe)
        except Exception as e:
            errmsg = Utilities.last_exception_info()
            warnings.warn(errmsg)
            raise RuntimeError(e)



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
        finally:
            if verbosity > 1:
                print('Done, closing <{0}>'.format(datetime.datetime.now()))
            zf.close()

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
            nowstr = datetime.datetime.now().strftime("%Y-%m-%d__%H_%M_%S")
            outfilename = basename + sep + nowstr + ext
            if not os.path.exists(outfilename):
                break
        if verbosity > 0:
            print("Creating '{0}'".format(outfilename))

        outfilepath = os.path.join(outdir, outfilename)
        return outfilepath

    @staticmethod
    def make_tempfilepath(folder, base, sep="_", ext="",
                          max_attempts=10,
                          exist_ok=True,
                          verbosity=0):
        if verbosity > 0:
            print("{0} {1}".format(Utilities.whoami(), Utilities.now()))
        if not os.path.isdir(folder):
            if verbosity > 0:
                print("trying to make folder {0}".format(folder))
            try:
                os.makedirs(folder, exist_ok=exist_ok)
            except Exception as e:
                msg = Utilities.last_exception_info()
                warnings.warn(msg)
                raise RuntimeError(e)
        attempt = 0
        while attempt < max_attempts:
            nowstr = Utilities.nowstr()
            filename = base + sep + nowstr + ext
            filepath = os.path.join(folder, filename)
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
            tempname = tempname + Utilities.nowstr()
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
    def __init__(self, verbosity=0):
        self.verbosity = verbosity

    def backup_folders(self, folders=None,
                       dest_drive=None,
                       dest_folder=None,
                       temp_folder=None,
                       logfilepath=None,
                       logfilename=None,
                       verbosity=0):
        """
        try to backup folders to a destination

        :param folders: list of folders to backup
        :param dest_drive: destination drive
        :param dest_folder: destination root directory
        :param logfilepath: path for log file
        :param logfilename: name of log file
        :param verbosity: level of diagnostics
        :return: 0 on success
        """

        ldict = locals()
        verbosity = max(self.verbosity, verbosity)
        Utilities.check_folders(folders)
        errmsg = ''
        req_param_types = {"folders": list,
                           "dest_drive": str,
                           "dest_folder": str,
                           "logfilepath": str,
                           "logfilename": str}
        for pname in req_param_types.keys():
            ptype = req_param_types[pname]
            val = ldict[pname]
            if val is None:
                errmsg += "No {0} specified".format(pname)
            elif not isinstance(val, ptype):
                errmsg += "{0} should be {1}, got {2}".format(pname, ptype, type(val))
        if len(errmsg) > 0:
            raise RuntimeError(errmsg)

        with open(logfilepath, mode="a") as fp:
            msg = "Backup starting {0}".format(datetime.datetime.now())
            fp.write(msg)
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
            print(msg)
            with open(logfilepath, mode="a") as fp:
                fp.write(msg)
            try:
                if verbosity > 0:
                    items = os.listdir(folder)
                    n = min(len(items), 7)
                    print("Found {0}".format(items[:n]))
                self.backup_folder(sourceroot=folder,
                                   destroot=destroot,
                                   tempfolder=temp_folder,
                                   testing=False,
                                   verbosity=verbosity)
            except PermissionError as e:
                msg = Utilities.last_exception_info(verbose=verbosity)
                warnings.warn(msg)
                raise PermissionError(msg)
            except Exception as e:
                msg = Utilities.last_exception_info(verbose=verbosity)
                warnings.warn(e)
                raise RuntimeError(msg)
            else:
                msg = "Seems ok {0}".format(datetime.datetime.now())
            with open(logfilepath, mode="a") as fp:
                fp.write(msg)
        return 0

    def backup_folder(self, sourceroot,
                      destroot,
                      tempfolder=None,
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
        :param comp_thresh: threshold for compression
            if compression ratio less than this then don't compress
        :param compression: method for compression
        :param compresslevel: level of compression
        :param testing: switch for just testing process
        :param verbosity: level of diagnostics
        :return: 0 on success
        """
        argdict = locals()
        verbosity = max(verbosity, self.verbosity)

        if verbosity > 0:
            msg = "{0} <{1}>".format(Utilities.whoami(), Utilities.now())
            msg += "\n  sourceroot= {0} destfolder= {1}".format(sourceroot, destroot)
            msg += "testing: {0}".format(testing)
            print(msg)

        if tempfolder is None:
            tempfolder = os.path.splitext(__file__)[0] + "_temp"
        if not os.path.isdir(tempfolder):
            os.mkdir(tempfolder)
        if verbosity > 0:
            print("  tempfolder= {0}".format(tempfolder))

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
                print("{0}: {1}".format(xname, x))
            locals()[xname] = x

        pp_sourceroot = PurePath(sourceroot)
        if not pp_sourceroot.is_absolute():
            warnings.warn("sourceroot must be absolute, {0}".format(sourceroot))

        pp_destroot = PurePath(destroot)
        if not pp_destroot.is_absolute():
            warnings.warn("destroot must be absolute, {0}".format(destroot))

        if (sourceroot == destroot) or (pp_sourceroot == pp_destroot):
            msg = "sourceroot cannot be same as destfolder"
            msg += "Please choose a different destfolder so files will not be overwritten"
            raise RuntimeError(msg)

        Utilities.check_make_path(destroot, verbosity=verbosity)

        destfolder = os.sep.join(pp_destroot.parts[1:])

        # orig_drive = pp_sourcefolder.drive
        # orig_folder = os.sep.join(pp_sourcefolder.parts[1:])
        if True:
            pass
            # metafilepath = Utilities.make_metafilepath(outdir=destfolder,
            #                                           basename="backup_meta",
            #                                           ext=".pickle",
            #                                           verbosity=verbosity)
            # metafilename = os.path.split(metafilepath)[1]

            # with open(metafilepath, mode='wb') as meta_fp:
            #    pickle.dump(ddict, meta_fp)

        # Walk the entire folder tree and compress the files in each folder.

        for dirpath, _, filenames in os.walk(sourceroot, topdown=True):
            pp_dirpath = PurePath(dirpath)
            # dirdrive = pp_dirpath.drive
            dirfolder = os.sep.join(pp_dirpath.parts[1:])

            if verbosity > 0:
                print("  Adding files from '{0}' to '{1}'".format(dirpath, destfolder))

            for filename in filenames:
                try:
                    if verbosity > 0:
                        msg = "filename: {0}, dirpath: {1}".format(filename, dirpath)
                        print(msg)
                    file_base, file_ext = os.path.splitext(filename)
                    if include_exts is not None:
                        if file_ext not in include_exts:
                            if verbosity > 1:
                                print("  Skipping {0}, {1} not in include_exts".format(filename, file_ext))
                            continue
                    if exclude_exts is not None:
                        if file_ext in exclude_exts:
                            if verbosity > 1:
                                print("  Skipping {0}, {1}  in include_exts".format(filename, file_ext))
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

                    # now check and see if the dest folder exists
                    if os.path.isdir(this_dest_folder):
                        # if there is a folder there
                        #  check all the files int the folder
                        #  to see if one of the fils sha_256 matches the source's
                        #  if so, contents the same and no need to backup
                        # NOTE: should I just check the lastest file?
                        dest_files = os.listdir(this_dest_folder)
                        for dfile in dest_files:
                            dpath = os.path.join(this_dest_folder, dfile)
                            dext = os.path.splitext(dfile)[1]
                            if dext == "zip":
                                # have to unzip to check
                                temppath = Utilities.unzip_to_temp(dpath,
                                                                   tempfolder=tempfolder)
                                dest_sha256 = Utilities.sha_256(temppath, size=4096)
                            else:
                                dest_sha256 = Utilities.sha_256(dpath, size=4096)

                            if source_sha256 == dest_sha256:
                                # then the same contents are already there
                                msg = "no need to backup {0}, {1} there with same contents".format(filename, dfile)
                                warnings.warn(msg)
                                continue

                    # at this point we need to backup
                    if verbosity > 0:
                        print("  backing up {0} from {1} to {2}".format(filename, dirpath,
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
                        Utilities.create_new_zip(sourcepath, zipfilepath)
                        zfile = zipfile.ZipFile(zipfilepath, mode='r')
                        nzipelems = len(list(zfile.infolist()))
                        if nzipelems > 1:
                            msg = "Uh-Oh, {0} elements in zipfile {1}".format(nzipelems, zipfilepath)
                            warnings.warn(msg)
                        zfile.close()
                        return zipfilepath
                    zipfilepath = zipit(sourcepath, tempfolder, verbosity=verbosity)
                    orig_size = os.path.getsize(sourcepath)
                    comp_size = os.path.getsize(zipfilepath)
                    comp_ratio = np.nan
                    if orig_size == 0:
                        warnings.warn("{0} in {1} size is {2}".format(filename, dirpath, orig_size))
                        continue
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
                                                                 base="",
                                                                 ext=this_ext,
                                                                 verbosity=verbosity)
                    # copy source to destination
                    shutil.copy(infilepath, dest_file_path)

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
                    meta_file_path = Utilities.make_tempfilepath(this_dest_folder,
                                                                 base="meta",
                                                                 ext=".txt",
                                                                 verbosity=verbosity)
                    # write the meta_dict to a file in dest folder
                    with open(meta_file_path, mode="w") as fp:
                        for key in meta_dict.keys():
                            fp.write("{0}: {1}\n".format(key, meta_dict[key]))

                    if verbosity > 0:
                        msg = "filename: {0}, filepath: {1}".format(filename, sourcepath)
                        msg += ", osize= {0}, csize= {1}".format(orig_size, comp_size)
                        msg += ", compressed= {0}".format(compressed)
                        msg += "\n infilepath: {0} dest folder: {1}".format(infilepath, this_dest_folder)
                        # print("sha_256= {0}".format(ddict['sha256']))
                        print(msg)

                    if compressed:
                        # remove the temporary zipfile
                        if os.path.isfile(zipfilepath):
                            try:
                                os.remove(zipfilepath)
                            except Exception as e:
                                msg = Utilities.last_exception_info()
                                warnings.warn(msg)
                                raise RuntimeError(e)
                        else:
                            msg = "can't find zipfile {0}".format(zipfilepath)
                            raise RuntimeError(msg)                    
                except Exception as e:
                    err_msg = Utilities.last_exception_info()
                    warnings.warn(err_msg)
                    raise RuntimeError(e)
        if verbosity > 0:
            print("Done")
        # meta_fp.close()
        return 0

    @staticmethod
    def recover(folder,
                # meta_filename,
                filelist,
                outdir,
                # create_outdir=False,
                # chunk_size = 10**6,
                # overwrite=False,
                # testing=True,
                verbosity=0):

        if not os.path.isdir(folder):
            warnings.warn("{0} is not a folder".format(folder))
            return None

        meta = Utilities.get_meta(folder, meta_filename)

        if not meta:
            return None

        if len(meta) == 1:
            warnings.warn("No file_info records")
            return None

        # res = Utilities.check_outdir(outdir, create=create_outdir, verbosity=0)

        filemap = {}
        for i, e in enumerate(meta[1:]):
            filemap[e['filename']] = i+1
        for filename in filelist:
            if filename in filemap.keys():
                ei = filemap[filename]
                msg = "Found {0} as entry {1}".format(filename, ei)
                print(msg)
                file_info = meta[ei]
                print(file_info)
                if file_info['compressed']:
                    outfilepath = Utilities.make_tempfilepath(outdir, base="temp", ext=".zip",
                                                              verbosity=verbosity)
                else:
                    outfilepath = os.path.join(outdir, file_info['filename'])
                print("outfilepath= {0}".format(outfilepath))
                outfilepath = os.path.abspath(outfilepath) # make sure folder is absolute
                print("outfilepath= {0}".format(outfilepath))
                infilename = file_info['sha256']
                infilepath = os.path.join(folder, infilename)
                if not os.path.isfile(infilepath):
                    warnings.warn("Cannot fine backup file {0} in {1}".format(infilename, folder))
                    continue
                try:
                    if verbosity > 0:
                        print("copying {0} to {1}".format(infilepath, outfilepath))
                        shutil.copy(infilepath, outfilepath)
                except Exception as e:
                    (extype, exval, tb) = sys.exc_info()
                    warnings.warn("extype= {0}, exval= {1}\n {2}".format(extype, exval, tb))

                if file_info['compressed']:
                    zipfilepath = outfilepath
                    outfilepath = os.path.join(outdir, file_info['filename'])
                    print("outfilepath {0}".format(outfilepath))
                if verbosity > 0:
                    print("Unzipping {0} to {1}".format(zipfilepath, outfilepath))

                zfile = zipfile.ZipFile(zipfilepath, mode='r')
                for zm in zfile.infolist():
                    print(zm)
                try:
                    zipname = file_info['zipname']
                    print("zipname= {0}  outfilepath= {1}".format(zipname, outfilepath))
                    zfile.extract(member=zipname,
                                  path=outfilepath, pwd=None)
                except Exception as e:
                    (extype, exval, tb) = sys.exc_info()
                    warnings.warn("extype= {0}, exval= {1}\n {2}".format(extype, exval, tb))
                    raise Exception(e)
                zfile.close()
                os.remove(zipfilepath)
          #with open(infilepath, mode='rb') as ifp:
          #  with open(outfilepath, mode="wb") as ofp:
          #    while True:
          #      ifp.read()
        else:
            msg = "No entry for {0}".format(filename)
            warnings.warn(msg)
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
    # initialize parameters
    bfolders = [
                # os.path.join("C:\\", "dev"),
                # os.path.join("C:\\", "Users", os.getenv("USERNAME"), "OneDrive", "dev"),
                # os.path.join("C:\\", "Users", os.getenv("USERNAME"), "enter1"),
                # os.path.join("C:\\", "Users", os.getenv("USERNAME"), "enter2"),
                # os.path.join("C:\\", "Users", os.getenv("USERNAME"), "OneDrive", "Desktop"),
                #os.path.join("C:\\", "Users", os.getenv("USERNAME"), "OneDrive", "Documents"),
                # os.path.join("C:\\", "Users", os.getenv("USERNAME"), "OneDrive", "Pictures"),
                os.path.join("C:\\", "Users", os.getenv("USERNAME"), "Documents"),
                os.path.join("C:\\", "Users", os.getenv("USERNAME"), "Downloads"),
                os.path.join("C:\\", "Users", os.getenv("USERNAME"), "Videos"),
                os.path.join("C:\\", "Users", os.getenv("USERNAME"), "Music"),
                ]
    dest_drive = "G:\\"

    dest_folder = os.path.join(dest_drive, os.environ['COMPUTERNAME'])
    logfilename = "backup_log" + "_" + Utilities.nowstr() + ".txt"
    logfilepath = logfilename

    # create instance of class
    GB = GitBack(verbosity=1)
    # backup folders
    res = GB.backup_folders(folders=bfolders,
                            dest_drive=dest_drive,
                            dest_folder=dest_folder,
                            logfilepath=logfilepath,
                            logfilename=logfilename,
                            verbosity=1)

    # zipfilepath = os.path.join('F:\\', 'backup', 'temp_2021-01-22__10_42_13.zip')
    # zfile = zipfile.ZipFile(zipfilepath, mode='r')
    # zfile.filename
    # zfile.getinfo(zfile.filename)

    # GB.backup_folder()
    # meta_folder = "backup"
    # files = os.listdir(meta_folder)
    # meta_files = [f for f in files if f.endswith("pickle")]

    meta_folder = "backup"
    files = os.listdir(meta_folder)
    meta_files = [f for f in files if f.endswith("pickle")]
    meta_filename = meta_files[0]
    print(meta_filename)

    # print_meta_info(folder=meta_folder, filename=meta_filename, fields=[''])
    meta_fields = Utilities.get_meta_fields(meta_folder, meta_filename)

    minfo = Utilities.get_meta_info(folder=meta_folder, filename=meta_filename, meta_fields=None,
                                  file_info_fields=['filename', 'zipname', 'orig_size'])
    print(minfo)

    # GB.recover(folder=meta_folder, meta_filename=meta_filename,
    #           filelist=['mail-loop.PNG'],
    #           outdir='recovered', create_outdir=True,
    #           overwrite=True, testing=False, verbosity=1)

    if 'verb' in locals().keys():
        meta_filename = "backup_meta_1.pickle"
        meta_folder = "backup"
        #meta = Utilities.import_backup_metafile(folder=meta_folder, filename=meta_filename)

