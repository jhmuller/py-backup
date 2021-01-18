#! python3
# backupToZip.py
# Copies an entire folder and its contents into
# a zip file whose filename increments.

import zipfile, os
import hashlib
import zlib
import pickle
from collections import OrderedDict

def sha_256(fpath, size=4096):
    m = hashlib.sha256()
    with open(fpath, mode='rb') as fp:
        for chunk in iter(lambda: fp.read(size), b''):
            m.update(chunk)
    return m.hexdigest()

def backup(folder, include_exts=None,
                exclude_exts=None,
                outpath=None,
               ofp=None,
                recursive = False,
                testing=False,
                verbosity=0):
    # Backup the entire contents of "folder" into a zip file.

    for xname in ('include_exts', 'exclude_exts'):
        x = locals()[xname]
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

    folder = os.path.abspath(folder) # make sure folder is absolute

    # Figure out the filename this code should used based on 
    # what files already exist.
    if not ofp:
        number = 1
        outname = ""
        pathleft = folder
        while True:
            pathleft, tail = os.path.split(pathleft)
            if len(tail) == 0:
                break
            outname = tail + "__" + outname
        if verbosity > 0:
            print("outname= {0}".format(outname))

        while True:
            outfilename = os.path.basename(outname) + str(number) + '.pickle'
            if not os.path.exists(outfilename):
                break
            number = number + 1
        if verbosity > 0:
            print("Creating '{0}'".format(outfilename))

        if outpath is not None:
            if not os.path.isdir(outpath):
                print("{0} not a dir, trying to create".format(outpath))
                os.makedirs(outpath)
                if not os.path.isdir(outpath):
                    msg = "Cannot make dir= '{0}'".format(outpath)
                    raise RuntimeError(msg)
        else:
            outpath = os.getcwd()
        outfilepath = os.path.join(outpath, outfilename)

    #backupZip = zipfile.ZipFile(zipFilename, 'w')
        ofp = open(outfilepath, mode='wb')
            # Walk the entire folder tree and compress the files in each folder.


    for foldername, subfolders, filenames in os.walk(folder):
        if verbosity > 0:
            print("Adding files in '{0}'".format(foldername))
        # Add the current folder to the ZIP file.
        # recursive call
        backup(foldername,include_exts=include_exts,
            exclude_exts=exclude_exts,
            outpath=outpath,   ofp=ofp,   testing=testing,
               recursive=True,
            verbosity=verbosity)
        # Add all the files in this folder to the ZIP file.
    for filename in filenames:
        base, ext = os.path.splitext(filename)
        if include_exts is not None:
            if ext not in  include_exts:
                if verbosity > 1:
                    print("  Skipping {0}, {1} not in include_exts".format(filename))
                continue
        if exclude_exts is not None:
            if ext in exlude_exts:
                if verbosity > 1:
                    print("  Skipping {0}, {1}  in include_exts".format(filename))
                continue
        if filename.startswith(os.path.basename(folder) + '_') and filename.endswith('.zip'):
            continue # don't backup the backup ZIP files
        filepath = os.path.join(folder, filename)
        if verbosity > 0:
            print("  adding {0}".format(filename))
        if not testing:
            res = OrderedDict()
            res[filepath] = {}
            with open(filepath, mode='rb') as fp:
                orig_data = fp.read()
            comp_data = zlib.compress(orig_data)
            res[filepath]['data'] = comp_data
            res[filepath]['sha256'] = sha_256(filepath, size=4096)
            res[filepath]['ctime'] = os.path.getctime(filepath)
            res[filepath]['mtime'] = os.path.getmtime(filepath)
            pickle.dump(res, ofp)
                    #backupZip.write(os.path.join(foldername, filename))
    if not recursive:
        if verbosity > 0:
            print("Done")
        ofp.close()

if __name__ == "__main__":
    bpath = os.path.join("C:\\", "Users", "jmull", "OneDrive", "Pictures")
    print("Path= {0}".format(bpath))
    N = 10
    print("files: {0}".format(os.listdir(bpath)[:N]))
    backup(bpath, testing=False, verbosity=1)
