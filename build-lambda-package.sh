#!/bin/bash
TEMPLATE_FILE="dynatrace-aws-log-forwarder.yaml"

LAMBDA_BUILD_DIR="temp-package-build"
LAMBDA_ZIP_NAME="dynatrace-aws-log-forwarder.zip"

set -ex

rm -f $LAMBDA_ZIP_NAME
rm -rf $LAMBDA_BUILD_DIR


# PREPARE LAMBDA ZIP

mkdir $LAMBDA_BUILD_DIR

# add lambda source
cp -r src/* $LAMBDA_BUILD_DIR

# add dependencies
pip3 install -r src/requirements.txt --target $LAMBDA_BUILD_DIR

# create lambda ZIP
cd $LAMBDA_BUILD_DIR
zip -r ../$LAMBDA_ZIP_NAME *
cd ..
rm -rf $LAMBDA_BUILD_DIR
