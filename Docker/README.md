## Docker version

Either run a packaged version from jonakarl/monroe-cli or from a local build.

### Local build  
```
sed -i.bak 's#CONTIANER=jonakarl/monroe-cli#CONTIANER=monroe-cli#g' monroe.sh
./build.sh
./monroe.sh setup <cert_path> <result_path>
```

### Prepackaged build   
```
./monroe.sh setup <cert_path> <result_path>
```

All other commands are equivalent to the original monroe-cli (they are passed verbatim to the monroe-cli script inside the container)

### Caveates
If you remove <result_path> you need to rerun ./monroe.sh setup <cert_path> <result_path>
