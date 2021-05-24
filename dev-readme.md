
## Notes for developers
### Build lambda release package
Run

```
./build-release-package.sh
```

In case of errors, try to run it in virtualenv to provide clean Python environment.

### Build & deploy public release package 

To build a new release, a git tag "release.*" on selected commit is required. 

You can either:
* push the tag manually, or 
* use GitHub *Draft new release* UI that can create for you the tag you specify together with the release:
https://github.com/dynatrace-oss/dynatrace-aws-log-forwarder/releases/new

The tag presence then triggers entire travis pipeline build and also creates a new release package:

https://github.com/dynatrace-oss/dynatrace-aws-log-forwarder/releases

For deployment, use one-liner from README to use the latest release, or adapt it for a specific version.

### Run unit tests in terminal

```
cd src 
python3 -m pytest -v ../tests/unit
```

### Run pylint in terminal

```
cd src 
python3 -m pylint --rcfile=../pipeline/pylint.cfg $(find . -name "*.py")
```
