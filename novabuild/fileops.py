# -*- coding: utf-8 -*- ex:set ts=4 sw=4 et:

import os
import shutil


def _copy_or_render(srcname, dstname, env, tpl_vars):
    if not srcname.endswith('.j2'):
        # Will raise a SpecialFileError for unsupported file types
        shutil.copy2(srcname, dstname)
        return
    
    dstname = dstname[:-3]

    open(dstname, 'w').write(env.get_template(srcname).render(**tpl_vars))
    shutil.copystat(srcname, dstname)


def copytree_j2(src, dst, env, tpl_vars):
    names = os.listdir(src)

    os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.islink(srcname):
                os.symlink(os.readlink(srcname), dstname)
            elif os.path.isdir(srcname):
                copytree_j2(srcname, dstname, env, tpl_vars)
            else:
                _copy_or_render(srcname, dstname, env, tpl_vars)
        # catch the Error from the recursive copytree so that we can continue
        # with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error, errors
