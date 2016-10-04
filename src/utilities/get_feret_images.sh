

DESTINATION_DIR=/Users/penn/galvanize/enhancer/data
FERETCOLOR_DIR=/Users/penn/galvanize/enhancer/data/colorferet

cd $DESTINATION_DIR
mkdir -p feret/originals/images
mkdir -p feret/originals/smaller
mkdir -p feret/originals/thumbnails

cd $FERETCOLOR_DIR"/colorferet/dvd1/data/images"
mv */* $DESTINATION_DIR"/feret/originals/images"

cd $FERETCOLOR_DIR"/colorferet/dvd1/data/smaller"
mv */* $DESTINATION_DIR"/feret/originals/smaller"

cd $FERETCOLOR_DIR"/colorferet/dvd1/data/thumbnails"
mv */* $DESTINATION_DIR"/feret/originals/thumbnails"

cd $DESTINATION_DIR"/feret/originals/images"
bzip2 -d *
cd $DESTINATION_DIR"/feret/originals/smaller"
bzip2 -d *
cd $DESTINATION_DIR"/feret/originals/thumbnails"
bzip2 -d *

