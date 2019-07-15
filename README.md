# rpi

:warning: This is very experimental

:warning: Works with development version of PlatformIO only (tested with `v4.0.0a16`)

Crystal plugin for use with [platformio](https://platformio.org). Allows writing code in Crystal targeting RaspberryPi (by default).

## Installation

1. Add the dependency to your `shard.yml`:

   ```yaml
   dependencies:
     rpi:
       github: unn4m3d/rpi
   ```

2. Run `shards install`

## Usage

Example platformio.ini configuration:

:warning: **(Linux)** You **MUST** use `https://github.com/unn4m3d/platform-linux_arm` as a platform in order to compile your C/C++ code because PlatformIO doesn't provide an `arm-unknown-linux-gnueabihf` toolchain for linux x86_64

```ini

[platformio]
env_default = rpi2

[env]
extra_scripts = pre:lib/rpi/platformio_script.py
crystal_target = main # Target should be specified in shard.yml
crystal_build_flags = -Dfoo
crystal_arch = arm-unknown-linux-gnueabihf # default
crystal_shards_bin = shards # default

[env:rpi2]
platform = https://github.com/unn4m3d/platform-linux_arm
board = raspberrypi_2b
```

## RaspberryPi environment

Before running your program you need to setup your Raspberry Pi environment. This step is different for different systems. **This example is for Raspbian stretch (oldstable)**:


```sh
# Install required packages
apt update
apt install git build-essential libpcre3-dev libevent-dev autoconf automake libtool

# We need to create links to some libs
# I don't know if version incompatibility will break your program, but regex tests seem to work
ln -s /lib/arm-linux-gnueabihf/libpcre.so.3 /lib/libpcre.so.1
ln -s /usr/lib/arm-linux-gnueabihf/libevent.so /lib/libevent-2.2.so.1

# We need to build libgc and libatomic_ops from source
# Crystal requires libgc >= 7.6.0
# Raspbian stretch provides 7.4 in official repo
git clone https://github.com/ivmai/bdwgc
cd bdwgc
git clone https://github.com/ivmai/libatomic_ops
autoreconf -vif
./configure
make
make install
ln -s /usr/local/lib/libgc.so /lib/libgc.so.1

# We also need libatomic_ops.so.1
cd libatomic_ops
autoreconf -vif
./configure
make
cd src
gcc -shared -o libatomic_ops.so *.o
cp libatomic_ops.so /lib
ln -s /lib/libatomic_ops.so /lib/libatomic_ops.so.1

# Alternatively, you can cross-compile libgc and libatomic ops on more powerful machine and then copy it to your RPi
# It should be faster to build, but probably harder to setup cross-compilation environment
```

## Contributing

1. Fork it (<https://github.com/unn4m3d/rpi/fork>)
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request

## Contributors

- [unn4m3d](https://github.com/unn4m3d) - creator and maintainer
