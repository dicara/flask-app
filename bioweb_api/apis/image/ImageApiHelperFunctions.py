import os
import tarfile

from bioweb_api.apis.ApiConstants import VALID_IMAGE_EXTENSIONS


def check_tar_structure(tar_path, valid_dir_name):
    """
    Verify that tar file has a single directory with appropriate name
    in it's root and that this directory contains valid image files.

    @param tar_path:        String of tar file path
    @param valid_dir_name:  String specifying valid root directory name
    @return:                Bool
    """
    # verify that file is tar file
    if not tarfile.is_tarfile(tar_path):
        return 'Not a tar file.'

    # open file and get members
    tf = tarfile.open(tar_path)
    members = tf.getmembers()
    tf.close()

    # separate members into root and non root
    root_members     = [m for m in members if os.path.split(m.name)[0] == '']
    valid_root_dir   = [m for m in root_members if m.isdir() and m.name == valid_dir_name]
    non_root_members = [m for m in members if os.path.split(m.name)[0] != '']
    filter_func      = lambda m: os.path.basename(m.name).endswith(tuple(VALID_IMAGE_EXTENSIONS)) and \
                            not os.path.basename(m.name).startswith('.')
    tar_images       = filter(filter_func, non_root_members)

    # verify that there are no other files in tar root except valid directory
    if len(root_members) != 1 or not valid_root_dir:
        return 'Tar root must have a single folder named "%s".' % valid_dir_name

    # verify that root dir has images
    elif not tar_images:
        return 'Tar file has no images.'

    # verify non root members are image files
    for member in non_root_members:
        ext = os.path.splitext(member.name)[1][1:]
        if not member.isfile() or ext not in VALID_IMAGE_EXTENSIONS:
            return 'Tar contains invalid files.'

def get_number_imgs(tar_path):
    """
    Return the image count within a tar file with a valid structure.
    Tar should be verified by check_tar_structure function first.

    @param tar_path:        String of tar file path
    @return:                Integer specitying image count
    """
    # open file and get members
    tf = tarfile.open(tar_path)
    members = tf.getmembers()
    tf.close()

    # images are non-hidden files that end with valid extension
    files_names = [os.path.basename(m.name) for m in members if m.isfile()]
    filter_func = lambda file_name: file_name.endswith(tuple(VALID_IMAGE_EXTENSIONS)) and \
                                not file_name.startswith('.')
    return len(filter(filter_func, files_names))
