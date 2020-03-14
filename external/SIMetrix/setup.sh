# Download the repository and compile
git clone https://github.com/igorbrigadir/simetrix
cd simetrix
mvn package

# Copy the necessary items to this directory
cp simetrix/target/simetrix-1.0-SNAPSHOT.jar simetrix.jar
cp -r simetrix/src/main/resources/data .
