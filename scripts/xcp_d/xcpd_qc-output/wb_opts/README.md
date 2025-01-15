# First download the spec 32k FS LR file from MSC Repo

dir=`pwd`
cd ${dir}
git clone https://github.com/MidnightScanClub/MSCcodebase.git

cd MSCcodebase
rm -rf Analysis/
rm -rf Processing/

# To view ptseries, dseries and dscalar images in wb_view, load Conte69_32k_fs_LR.wb.spec file
