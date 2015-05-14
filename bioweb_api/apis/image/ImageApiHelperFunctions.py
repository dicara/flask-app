import os
import tarfile

from bioweb_api.apis.ApiConstants import VALID_IMAGE_EXTENSIONS

def check_ham_tar_structure(tar_path, valid_dir_name):
    """
    Verify that tar file has a single directory with appropriate name
    in it's root and that this directory contains valid image files.

    @param tar_path:        String of tar file path
    @param valid_dir_name:  String specifying valid root directory name
    @return:                Tuple containing error message if any and
                            image count if no errors were encountered.
    """
    # verify that file is tar file
    if not tarfile.is_tarfile(tar_path):
        return 'Not a tar file.', None

    # open file and get members
    tf = tarfile.open(tar_path)
    members = tf.getmembers()
    tf.close()

    # verify that there are no other files in tar root except a single directory
    valid_root_members = [m for m in members if os.path.split(m.name)[0] == '' and m.isdir()]
    if len(valid_root_members) != 1:
        return 'Tar root must have a single directory.', None

    # verify tar root directory has a valid name
    valid_root_dir = [m for m in valid_root_members if m.name == valid_dir_name]
    if not valid_root_dir:
        return 'Tar root folder must be named "%s".' % valid_dir_name, None

    # check if directory is empty
    non_root_members = [m for m in members if os.path.split(m.name)[0] != '']
    if not non_root_members:
        return 'Image directory is empty.', None

    # verify image directory contents
    img_count = 0
    for member in non_root_members:
        base_name = os.path.basename(member.name)
        # check extension
        if not base_name.endswith(tuple(VALID_IMAGE_EXTENSIONS)):
            return 'Tar contains non-image files.', None
        # check file type
        elif not member.isfile():
            return 'Tar image folder has members that are not file.', None
        # osx tar files contain non-visible files containing metadata, ignore them
        elif base_name.startswith('.'):
            pass
        else:
            img_count += 1

    return '', img_count


def check_mon_tar_structure(tar_path, valid_dir_name):
    """
    Verify the contents of a monitor image stack.  The root directory
    must have a valid name and it must contain three directories named
    cropped_electrode_off, cropped_electrode_on, and uncropped.

    @param tar_path:        String of tar file path
    @param valid_dir_name:  String specifying valid root directory name
    @return:                Tuple containing error message if any and
                            image count if no errors were encountered.
    """
    # verify that file is tar file
    if not tarfile.is_tarfile(tar_path):
        return 'Not a tar file.', None

    # open file and get members
    tf = tarfile.open(tar_path)
    members = tf.getmembers()
    tf.close()

    # verify that there are no other files in tar root except a single directory
    valid_root_members = [m for m in members if os.path.split(m.name)[0] == '' and m.isdir()]
    if len(valid_root_members) != 1:
        return 'Tar root must have a single directory.', None

    # verify tar root directory has a valid name
    valid_root_dir = [m for m in valid_root_members if m.name == valid_dir_name]
    if not valid_root_dir:
        return 'Tar root folder must be named "%s".' % valid_dir_name, None

    # check if directory contains three folders named cropped_electrode_off,
    # cropped_electrode_on, and uncropped.
    mon_dir_members = [m for m in members if os.path.split(m.name)[0] == valid_dir_name]
    mon_dir_files   = [m for m in mon_dir_members if not m.isdir]
    mon_dir_dirs    = [m for m in mon_dir_members if m.isdir]
    crop_ele_off    = [m for m in mon_dir_dirs if os.path.basename(m.name) == 'cropped_electrode_off']
    crop_ele_on     = [m for m in mon_dir_dirs if os.path.basename(m.name) == 'cropped_electrode_on']
    uncropped       = [m for m in mon_dir_dirs if os.path.basename(m.name) == 'uncropped']

    if mon_dir_files or \
       len(mon_dir_dirs) != 3 or \
       not crop_ele_on or \
       not uncropped or \
       not crop_ele_off:
        return '%s folder must contain directories named cropped_electrode_off,' \
        ' cropped_electrode_on, and uncropped' % valid_dir_name, None

    # get image count
    img_count = 0
    for member in members:
        base_name = os.path.basename(member.name)
        # osx makes non-visible files, ignore them
        if not base_name.startswith('.') and \
           member.isfile and \
           base_name.endswith(tuple(VALID_IMAGE_EXTENSIONS)):
            img_count += 1

    # make sure there are images
    if img_count == 0:
        return 'There are no images in this tar file', None

    return '', img_count


def extract_imgs(existing_tar, replay_dir_path):
    """
    Adds images from existing image files into a the replay tar file.

    @param existing_tar:    String specifying path to tar file containing image stacks
    @param tmp_path:        String specifying temporary directory to tar/untar
    """
    # extract incoming
    tf = tarfile.open(existing_tar)
    tf.extractall(replay_dir_path)
    tf.close()
