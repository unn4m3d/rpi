Import("env")
from platformio import util
from platformio.project.helpers import get_project_build_dir, get_project_dir
from platformio.project.config import ProjectConfig
from os.path import basename, join, relpath, abspath, isfile
from os import environ
import base64
import subprocess

config = ProjectConfig.get_instance(join(get_project_dir(), "platformio.ini"))

def get_envname():
    return base64.b64decode(ARGUMENTS["PIOENV"])

envname = get_envname()
print("PBD: %s, env : %s" % (relpath(get_project_build_dir()), envname))

def get_crystal_target():
    if config.has_option("env:" + envname, "crystal_target"):
        return config.get("env:" + envname, "crystal_target")
    else:
        return "main"

def get_crystal_build_flags():
    if config.has_option("env:" + envname, "crystal_build_flags"):
        return config.get("env:" + envname, "crystal_build_flags")
    else:
        return ""

def get_shards_binary():
    if config.has_option("env:" + envname, "crystal_shards_bin"):
        return config.get("env:" + envname, "crystal_shards_bin")
    else:
        return "shards"

def get_crystal_binary():
    if config.has_option("env:" + envname, "crystal_bin"):
        return config.get("env:" + envname, "crystal_bin")
    else:
        return "crystal"

def get_crystal_triple():
    if config.has_option("env:" + envname, "crystal_arch"):
        return config.get("env:" + envname, "crystal_arch")
    else:
        return "arm-unknown-linux-gnueabihf"

def get_crystal_lib_path():
    if config.has_option("env:" + envname, "crystal_path_extra"):
        return config.get("env:" + envname, "crystal_path_extra")
    else:
        return "./lib"


def add_compile_crystal_target():
    input_file = get_crystal_target()
    output_obj_file = join(get_project_build_dir(), envname, "__crystal_{}".format(relpath(input_file)))
    print("output file : %s" % output_obj_file)

    shard_yml = isfile("shard.yml")

    compile = "{bin} build {crystal_target} --verbose -o{output} --cross-compile --target={target} {flags}".format(
        bin = get_shards_binary() if shard_yml else get_crystal_binary(),
        crystal_target = input_file if shard_yml or isfile(input_file) else "src/%s.cr" % input_file ,
        output = output_obj_file,
        target = get_crystal_triple(),
        flags = get_crystal_build_flags()
    )

    output_obj_file = output_obj_file + ".o"

    install_shards = "{bin} update".format(bin = get_shards_binary())
    install_dep = None

    if shard_yml:
        env.AlwaysBuild(env.Alias("install_shards", None, [install_shards]))
        install_dep = "install_shards"

    env.Command(output_obj_file, install_dep, [compile])

    env.Depends("%s/%s/program" % (get_project_build_dir(), envname), output_obj_file)
    env.Append(PIOBUILDFILES=abspath(output_obj_file))
    #env.Append(PIOBUILDFILES=abspath("./lib/rpi/libraries/libgc.a"))
    #libgc = abspath("./lib/rpi/libraries/libgc.a")
    libgc = "-lgc"
    libpath = join(get_crystal_lib_path(), "rpi", "libraries")
    env.Append(LINKFLAGS="-L%s -rdynamic -lpcre -lpthread -levent -lrt -ldl %s -l:libatomic_ops.so.1" % (libpath, libgc))

def add_compile_crystal_extension():
    env.Append(SRC_FILTER="-<*/ext/sigfault.c>")
    #libname = join(get_project_build_dir(), get_envname(), "libcrystal.a")
    #libname = "crystal"
    libname = join(get_project_build_dir(), get_envname(), "crystal.o")
    env.Object(libname, ["src/ext/sigfault.c"])
    env.Append(LINKFLAGS=libname)
    #env.Append(PIOBUILDFILES=abspath(libname))
    env.Depends("%s/%s/program" % (get_project_build_dir(), envname), libname)

def export_crystal_path():
    if config.has_option("env:%s" % envname, "crystal_path_extra"):
        old_path = subprocess.check_output(['crystal', 'env', 'CRYSTAL_PATH']).rstrip()
        env.AppendENVPath('CRYSTAL_PATH', old_path )
        env.AppendENVPath('CRYSTAL_PATH', get_crystal_lib_path())
        print("CRYSTAL_PATH=%s" % env['ENV']['CRYSTAL_PATH'])

export_crystal_path()
add_compile_crystal_extension()
add_compile_crystal_target()
