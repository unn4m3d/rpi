Import("env")
from platformio import util
from platformio.project.helpers import get_project_build_dir
from os.path import basename, join, relpath, abspath
import base64

config = util.load_project_config()

def get_envname():
    return base64.b64decode(ARGUMENTS["PIOENV"])

envname = get_envname()

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

def get_crystal_triple():
    if config.has_option("env:" + envname, "crystal_arch"):
        return config.get("env:" + envname, "crystal_arch")
    else:
        return "arm-unknown-linux-gnueabihf"

def add_compile_crystal_target():
    input_file = get_crystal_target()
    output_obj_file = join(get_project_build_dir(), envname, "__crystal_{}".format(relpath(input_file)))
    print("output file : %s" % output_obj_file)

    compile = "{bin} build {crystal_target} -v -o{output} --cross-compile --target={target} {flags}".format(
        bin = get_shards_binary(),
        crystal_target = input_file,
        output = output_obj_file,
        target = get_crystal_triple(),
        flags = get_crystal_build_flags()
    )

    output_obj_file = output_obj_file + ".o"

    install_shards = "{bin} update".format(bin = get_shards_binary())

    env.AlwaysBuild(env.Alias("install_shards", None, [install_shards]))
    env.Alias(relpath(output_obj_file), "install_shards", [compile])
    env.Depends("%s/%s/program" % (get_project_build_dir(), envname), relpath(output_obj_file))
    env.Append(PIOBUILDFILES=abspath(output_obj_file))
    #env.Append(PIOBUILDFILES=abspath("./lib/rpi/libraries/libgc.a"))
    #libgc = abspath("./lib/rpi/libraries/libgc.a")
    libgc = "-lgc"
    env.Append(LINKFLAGS="-L./lib/rpi/libraries -rdynamic -lpcre -lpthread -levent -lrt -ldl %s -l:libatomic_ops.so.1" % libgc)

def add_compile_crystal_extension():
    libname = join(get_project_build_dir(), get_envname(), "libcrystal.a")
    #libname = "crystal"
    env.StaticLibrary(libname, ["src/ext/sigfault.c"])
    env.Append(LINKFLAGS=libname)
    #env.Append(PIOBUILDFILES=abspath(libname))
    env.Depends("%s/%s/program" % (get_project_build_dir(), envname), libname)

add_compile_crystal_extension()
add_compile_crystal_target()
