
echo "Upload untouched compressed FERET dataset to s3"
filename="test.txt"
bucket="s3://enhancer/feret/"
aws s3 cp $filename $bucket"original-"$filename --storage-class=STANDARD_IA --dryrun