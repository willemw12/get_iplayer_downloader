import subprocess

# For non-git downnloaded version
_version = "0.3-x"

def _version():
    """ Get version from git, if possible. """
    try:
        # Linux specific
        return subprocess.check_output("echo -n $(git describe --tags | head -1)", shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        pass
    return _version

# Check if called from the interpreter
#if sys.argv[0]:
#    __program_name__ = os.path.splitext(os.path.basename(sys.argv[0]))[0]
#else:
__program_name__ = "get_iplayer_downloader"

__description__ = "Download utility for the BBC get_iplayer program"
__long_description__ = "get_iplayer_downloader is a graphical version of the command \"get_iplayer --tree\", followed by \"get_iplayer --pid\" or \"get_iplayer --info\""
__version__ = _version()
__authors__ = "willemw12"
__emails__ = "willemw12@gmail.com"
__url__ = "https://github.com/willemw12/get_iplayer_downloader"
__license__ = "GPLv3"
# BSD, MacOS, Windows untested
__platforms__ = "Linux"
