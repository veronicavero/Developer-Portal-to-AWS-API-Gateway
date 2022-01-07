#!/usr/bin/env bash

# modify the value whenever push a new version
LastVersion=6

[ ! -d $LastVersion ] && mkdir $LastVersion
mkdir $LastVersion/lambda
mkdir $LastVersion/lambda/layers
cd ../lambda

# developer portal management lambda
zip ../scripts/$LastVersion/lambda/DeveloperPortalManagement.zip DeveloperPortalManagement.py


