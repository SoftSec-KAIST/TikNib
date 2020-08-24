#!/bin/bash
ls | awk '{split($0,a,".yml"); print a[1]}' | xargs -i mv {}.yml {}_type.yml
