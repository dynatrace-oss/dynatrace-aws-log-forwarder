
## Notes for developers
### Build lambda release package
Run

```
./build-release-package.sh
```

In case of errors, try to run it in virtualenv to provide clean Python environment.

### Build & deploy to public repo: temporarily S3

upload to:
https://s3.console.aws.amazon.com/s3/buckets/dynatraceawslogforwarder?region=us-east-1&prefix=preview/&showversions=false

in Dynatrace Metrics Streaming Production (534730002411)
   localMetricsStreamDeveloperUser


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
