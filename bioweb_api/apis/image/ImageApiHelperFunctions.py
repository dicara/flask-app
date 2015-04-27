import os
import shutil
import tarfile

from bioweb_api.apis.ApiConstants import VALID_IMAGE_EXTENSIONS
from bioweb_api.utilities.io_utilities import silently_remove_tree


def check_tar_structure(tar_path, valid_dir_name):
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
        # osx tar files contain non-visible files containing metadata, allow them
        elif base_name.startswith('.'):
            pass
        else:
            img_count += 1

    return '', img_count


def add_imgs(replay_tar_file, existing_tar, tmp_path, stack_type):
    """
    Adds images from existing image files into a the replay tar file.

    @param replay_tar_file: Tarfile object that is writable.
    @param existing_tar:    String specifying path to tar file containing image stacks
    @param tmp_path:        String specifying temporary directory to tar/untar
    @param stack_type:      String specifying name of image type (will be name of root dir)
    """
    tf = tarfile.open(existing_tar)
    tf.extractall(tmp_path)

    replay_tar_file.add(os.path.join(tmp_path, stack_type), stack_type)
    silently_remove_tree(os.path.join(tmp_path, stack_type))

