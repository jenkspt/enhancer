

DESTINATION_DIR="/Users/penn/galvanize/enhancer/data/"
FERETCOLOR_DIR="/Users/penn/galvanize/enhancer/data/colorferet/"

IMG_SIZES=("images/" "smaller/" "thumbnails/")
# Make the folders to move all the original images
# so that they are all in one place

DEST=$DESTINATION_DIR"feret/original/"
for dir in $IMG_SIZES; do
	mkdir -p $DEST$dir
done


cd $FERETCOLOR_DIR"/colorferet/"
# Go into both dvd folders
for dvd in "dvd1/" "dvd2/"; do
	# In each dvd folder, go in to the image folders
	cd $dvd
	for size in $IMG_SIZES; do
		cd "data/"$size
		dest=$DEST$size
		# In each image folder go into each user folder
		for user in $( ls $size_dir ); do
			cd $user
			echo "Decompressing and moving contents of "$( pwd )
			bzip2 -dkfq *
			# In each user folder copy the decompressed file to the destination
			for img in $( ls *.ppm ); do
				mv -f $src$img $dest
			done

			cd ../
		done
		cd ../../
	done
	cd ../
done

