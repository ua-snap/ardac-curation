#!/bin/bash


WGET_VERSION=$(wget --version | grep -oie "wget [0-9][0-9.]*" | head -n 1 | awk '{print $2}')
if [ -z "$WGET_VERSION" ]
then
WGET_VERSION=PARSE_ERROR
fi

WGET_USER_AGENT="wget/$WGET_VERSION/esg/4.3.4-20230502-192705/created/2023-05-11T11:04:17-06:00"


##############################################################################
#
# Climate Data Gateway download script
#
#
# Generated by: NCAR Climate Data Gateway
#
# Template version: 0.4.7-wget-checksum
#
#
# Your download selection includes data that might be secured using API Token based
# authentication. Therefore, this script can have your api-token. If you
# re-generate your API Token after you download this script, the download will
# fail. If that happens, you can either re-download this script or you can replace
# the old API Token with the new one by going to the Account Home:
#
# https://www.earthsystemgrid.org/account/user/account-home.html
#
# and clicking on "API Token" link under "Personal Account". You will be asked
# to log into the application before you can view your API Token.
#
#
# Dataset
# ucar.ral.hydro.predictions.alaska.vic.daily
# 5b346036-ac94-4fc9-aa2d-4edc28030f83
# https://www.earthsystemgrid.org/dataset/ucar.ral.hydro.predictions.alaska.vic.daily.html
# https://www.earthsystemgrid.org/dataset/id/5b346036-ac94-4fc9-aa2d-4edc28030f83.html
#
# Dataset Version
# 1.0
# 7010a99e-535d-40d9-bd59-d2a17c75beef
# https://www.earthsystemgrid.org/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/version/1.0.html
# https://www.earthsystemgrid.org/dataset/version/id/7010a99e-535d-40d9-bd59-d2a17c75beef.html
#
##############################################################################

CACHE_FILE=.md5_results
MAX_RETRY=3


usage() {
    echo "Usage: $(basename $0) [flags]"
    echo "Flags is one of:"
    sed -n '/^while getopts/,/^done/  s/^\([^)]*\)[^#]*#\(.*$\)/\1 \2/p' $0
}
#defaults
debug=0
clean_work=1
verbose=1

#parse flags

while getopts ':pdvqko:' OPT; do

    case $OPT in

        p) clean_work=0;;       #	: preserve data that failed checksum
        o) output="$OPTARG";;   #<file>	: Write output for DML in the given file
        d) debug=1;;            #	: display debug information
        v) verbose=1;;          #       : be more verbose
        q) quiet=1;;            #	: be less verbose
        k) cert=1;;            #	: add --no-check-certificate
        \?) echo "Unknown option '$OPTARG'" >&2 && usage && exit 1;;
        \:) echo "Missing parameter for flag '$OPTARG'" >&2 && usage && exit 1;;
    esac
done
shift $(($OPTIND - 1))

if [[ "$output" ]]; then
    #check and prepare the file
    if [[ -f "$output" ]]; then
        read -p "Overwrite existing file $output? (y/N) " answ
        case $answ in y|Y|yes|Yes);; *) echo "Aborting then..."; exit 0;; esac
    fi
    : > "$output" || { echo "Can't write file $output"; break; }
fi

    ((debug)) && echo "debug=$debug, cert=$cert, verbose=$verbose, quiet=$quiet, clean_work=$clean_work"

##############################################################################


check_chksum() {
    local file="$1"
    local chk_type=$2
    local chk_value=$3
    local local_chksum

    case $chk_type in
        md5) local_chksum=$(md5sum "$file" | cut -f1 -d" ");;
        *) echo "Can't verify checksum." && return 0;;
    esac

    #verify
    ((debug)) && echo "local:$local_chksum vs remote:$chk_value"
    diff -q <(echo $local_chksum) <(echo $chk_value) >/dev/null
}

download() {

    if [[ "$cert" ]]; then
      wget="wget --no-check-certificate -c --user-agent=$WGET_USER_AGENT"
    else
      wget="wget -c --user-agent=$WGET_USER_AGENT"
    fi

    ((quiet)) && wget="$wget -q" || { ((!verbose)) && wget="$wget -nv"; }

    ((debug)) && echo "wget command: $wget"

    while read line
    do
        # read csv here document into proper variables
        eval $(awk -F "' '" '{$0=substr($0,2,length($0)-2); $3=tolower($3); print "file=\""$1"\";url=\""$2"\";chksum_type=\""$3"\";chksum=\""$4"\""}' <(echo $line) )

        #Process the file
        echo -n "$file ..."

        #are we just writing a file?
        if [ "$output" ]; then
            echo "$file - $url" >> $output
            echo ""
            continue
        fi

        retry_counter=0

        while : ; do
                #if we have the file, check if it's already processed.
                [ -f "$file" ] && cached="$(grep $file $CACHE_FILE)" || unset cached

                #check it wasn't modified
                if [[ -n "$cached" && "$(stat -c %Y $file)" == $(echo "$cached" | cut -d ' ' -f2) ]]; then
                    echo "Already downloaded and verified"
                    break
                fi

                # (if we had the file size, we could check before trying to complete)
                echo "Downloading"
                $wget -O "$file" $url || { failed=1; break; }

                #check if file is there
                if [[ -f "$file" ]]; then
                        ((debug)) && echo file found
                        if ! check_chksum "$file" $chksum_type $chksum; then
                                echo "  $chksum_type failed!"
                                if ((clean_work)); then
                                        rm "$file"

                                        #try again up to n times
                                        echo -n "  Re-downloading..."

                                        if [ $retry_counter -eq $MAX_RETRY]
                                        then
                                            echo "  Re-tried file $file $MAX_RETRY times...."
                                            break
                                        fi
                                        retry_counter=`expr $retry_counter + 1`

                                        continue
                                else
                                        echo "  don't use -p or remove manually."
                                fi
                        else
                                echo "  $chksum_type ok. done!"
                                echo "$file" $(stat -c %Y "$file") $chksum >> $CACHE_FILE
                        fi
                fi
                #done!
                break
        done

        if ((failed)); then
            echo "download failed"

            unset failed
        fi

    done <<EOF--dataset.file.url.chksum_type.chksum
'daymet_eb_1980.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1980.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'ea088309ffd36309e2ea1afcb0d364cf'
'daymet_eb_1981.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1981.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'ffa4bd526944226b341d5cb44a0b7908'
'daymet_eb_1982.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1982.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '6710d7876363b54f62b4c6746a4ccbe3'
'daymet_eb_1983.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1983.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '218ffffedd186008ab5f12a9e1743a7b'
'daymet_eb_1984.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1984.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'cc432b33302c60dd4bd26c71d2da361d'
'daymet_eb_1985.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1985.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '9049fbb61838577e8803e9cfa6db31eb'
'daymet_eb_1986.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1986.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'c886b28a069927372dd241c56b28d40d'
'daymet_eb_1987.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1987.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '145361a310e7f2bc9273a5ed44634a88'
'daymet_eb_1988.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1988.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'e6cfaf09f41fbf13f86eb114c1b94cd5'
'daymet_eb_1989.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1989.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '52975fa60bb85b0e5fde5877120dff08'
'daymet_eb_1990.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1990.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '09f95aa5bd99139c27c0ca69349fd234'
'daymet_eb_1991.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1991.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '7c1574e29646dd7dc19d660274c184f1'
'daymet_eb_1992.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1992.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '9f4538fc516d640eb76011f90261a176'
'daymet_eb_1993.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1993.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'bd6c04394409eb861233ba8d1f54211e'
'daymet_eb_1994.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1994.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '19522b2ddd12570050fadd25e6a272e7'
'daymet_eb_1995.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1995.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '40859ac79ae1bf24d7f926d6df74073a'
'daymet_eb_1996.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1996.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'cb7c6d61230bb96e82dc68b323aeeae8'
'daymet_eb_1997.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1997.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '0ce4e5a59658ac55ed03dac90c5860f7'
'daymet_eb_1998.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1998.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'bdab56e8b230b2db3381310faf93a4b3'
'daymet_eb_1999.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_1999.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'e4912501d03b6af5daaf2be3b43c6cb3'
'daymet_eb_2000.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2000.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'e162a29fb2756d80b9930fe315231fcc'
'daymet_eb_2001.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2001.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '37023b4810663e7616a2826e34c208b9'
'daymet_eb_2002.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2002.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '1601bfe1a187e6431bc3f685078599ea'
'daymet_eb_2003.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2003.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'ea6d36a8669bb393acf3a1b4d0aa6c07'
'daymet_eb_2004.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2004.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'da2efa3a75242b7b8e05fdd68178c1c9'
'daymet_eb_2005.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2005.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '67c894a57a6343ac5de521fbd5a83309'
'daymet_eb_2006.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2006.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '22c117b40172b93f01dc2f11232a9934'
'daymet_eb_2007.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2007.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'd05cfe3869a10c7d127dde90b1dd2801'
'daymet_eb_2008.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2008.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '6dde8ccfc05774f97862f93b3aea467f'
'daymet_eb_2009.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2009.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '8a5c8f130d6e5bbeb129c7234d9ed2a3'
'daymet_eb_2010.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2010.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '031f23e945ce2e11ba38c36157bcdaf8'
'daymet_eb_2011.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2011.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'fe40c35d5b2b0fb6a6582d970a4e8937'
'daymet_eb_2012.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2012.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '4ac0918152fe8e3fbe7162ff18d6a1ee'
'daymet_eb_2013.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2013.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '91cc3a7b62eeb0b4bddffed82d78d39c'
'daymet_eb_2014.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2014.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'd43f299cf87e1298d0d30a48e67e887b'
'daymet_eb_2015.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2015.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'a885b9198bb36b6ffa2247b4e93c0d36'
'daymet_eb_2016.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_eb_2016.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'c95a19536b779c593b72c64c8e005d2f'
'daymet_wf_1980.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1980.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '711afc37d63b735bf769b55a77b8d778'
'daymet_wf_1981.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1981.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '476942565518a2af560124af98fa554f'
'daymet_wf_1982.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1982.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'ca99202e46f6e54a1b16aeebfc177407'
'daymet_wf_1983.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1983.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'bc7c31c8e4551c74de0b828d37c21715'
'daymet_wf_1984.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1984.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '2d00e0d51875d6052e72ad71bc57eb90'
'daymet_wf_1985.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1985.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '68edc3b39d1e008a8295913b3b115df7'
'daymet_wf_1986.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1986.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '6eb9f404f6e2731ed77ae65a57c166e9'
'daymet_wf_1987.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1987.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '0cebf871e4080b8d87adef2c63598a5c'
'daymet_wf_1988.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1988.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'c75cb0aeec069f19b5ec11ae15b4d89e'
'daymet_wf_1989.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1989.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '8fbc9bee51406a03f8e2c2af66976fa8'
'daymet_wf_1990.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1990.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'b7d22cc500f0ad99f62fe5132f4a18e5'
'daymet_wf_1991.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1991.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'fb5f95a596dafcc2a8eeb0aec9a54e97'
'daymet_wf_1992.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1992.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '1e50b2c379da30a676e7afd87c69aa65'
'daymet_wf_1993.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1993.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '19a0ea3c3b6cd731551e42ccb7c519ea'
'daymet_wf_1994.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1994.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'c68def3c0da06a3216a72458cc25e9cb'
'daymet_wf_1995.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1995.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '3aa50ba05a140872019599c39e5a1a87'
'daymet_wf_1996.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1996.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '860929e3b9d53ab23e180fce14d07bfd'
'daymet_wf_1997.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1997.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'a48df7221088d206d62701dafd00ef3d'
'daymet_wf_1998.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1998.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '37673ea28c016285d78f2bc676c6c55c'
'daymet_wf_1999.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_1999.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '2016ee94b745e5236488064f719fc240'
'daymet_wf_2000.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2000.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '6e5fd2b4ff6632ef774c02ceaa8fa69a'
'daymet_wf_2001.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2001.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '56b9eb7d8a37d08e07e83f31596e1aa0'
'daymet_wf_2002.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2002.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '773a10e0692a62d811252b97720c1e27'
'daymet_wf_2003.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2003.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '928202206c1e130984f4bb71f4537d18'
'daymet_wf_2004.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2004.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '960a2f4ef02efd9560b86697c747f6de'
'daymet_wf_2005.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2005.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '6dafd1a5daa74e270a64c4735a4cb0e2'
'daymet_wf_2006.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2006.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '00e004d30f9f49ea90ceefd3df0fc14a'
'daymet_wf_2007.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2007.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '9725fe307ad48d869842ab366544a285'
'daymet_wf_2008.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2008.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'e0a21716c13e7c19189d41b2cd282bda'
'daymet_wf_2009.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2009.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '7923e12b06533c6b74a0fbaafd313d24'
'daymet_wf_2010.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2010.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'ada310b4d2ece8425cd6bf8fe1269405'
'daymet_wf_2011.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2011.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '482d298a5c96a8b63b1c825f88b1b758'
'daymet_wf_2012.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2012.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '10c79376f9253befb76f8b33a2ad5418'
'daymet_wf_2013.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2013.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '6ac26fbac2a6397ea291b2a7df1bb094'
'daymet_wf_2014.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2014.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'da4cae0bbaeda51539a030656400472e'
'daymet_wf_2015.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2015.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '860aade4aa22a7df7c9ec16b1c18dabd'
'daymet_wf_2016.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_wf_2016.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '6d3e3ab871d1e39e708000f9bff102dd'
'daymet_ws_1980.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1980.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '6749c18f1b8c653830af717c3d7848b1'
'daymet_ws_1981.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1981.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '78f305f17640b7a23007146b4965ab40'
'daymet_ws_1982.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1982.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'bd7aafcfc70dda9abdc1103f96ea9dbf'
'daymet_ws_1983.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1983.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '7329238f393bf68db691d349ebbe559a'
'daymet_ws_1984.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1984.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'ec10e9480badb10101e179c3bfd196e9'
'daymet_ws_1985.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1985.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '860de44cc95b689358a1ec989708269a'
'daymet_ws_1986.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1986.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '357f4e2831c000ae2824011638edc045'
'daymet_ws_1987.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1987.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'd6ff3a31a24572f198cdd4bdeae18c62'
'daymet_ws_1988.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1988.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '578688f7e1b346cb6fe68d9a5922dab3'
'daymet_ws_1989.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1989.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'e74dff934fdfa4f5f86e62bd201dd852'
'daymet_ws_1990.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1990.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '9951cbbe520a9a6539ffc3b5b469df8e'
'daymet_ws_1991.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1991.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '16410f6d2d0f99a95c1d7c8e4ac8fbf2'
'daymet_ws_1992.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1992.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '51182184455421301bb722752c0225ff'
'daymet_ws_1993.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1993.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '3cfbde5adb855371d7aa19febe71f27f'
'daymet_ws_1994.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1994.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'f141b83d33937f7613f33ffa1b2c7a28'
'daymet_ws_1995.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1995.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '5fa7ecf7a9ce64b71226fb140786784a'
'daymet_ws_1996.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1996.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '7db335b64b9702e1a2c18edc26df0903'
'daymet_ws_1997.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1997.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '976a0a2daf92feb6343156de129b8ecd'
'daymet_ws_1998.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1998.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '3bd6a9e445b2661f21347e6367e8df6c'
'daymet_ws_1999.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_1999.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '8b686bb70c86f96ac1e7b453930f0a92'
'daymet_ws_2000.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2000.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '9457bca6eac4a660875156946832ef04'
'daymet_ws_2001.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2001.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'b9ebcc03798394331e613b2e9d5e8f95'
'daymet_ws_2002.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2002.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '3be467a297441b7ca6cec09b2a3b38f3'
'daymet_ws_2003.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2003.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'e2983d96a3e1d4300437b2dd595787f6'
'daymet_ws_2004.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2004.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'ca218ac6931bd5792ea3f8e18bbdde73'
'daymet_ws_2005.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2005.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'e173d610f221466be6c8bf1ad058de44'
'daymet_ws_2006.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2006.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '8e75a8a22453af7ef89e53620d37bfd2'
'daymet_ws_2007.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2007.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '30dc294a7729aa745760114860f40c83'
'daymet_ws_2008.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2008.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'c42f870c284f57bb5b0c94b6967d6d2f'
'daymet_ws_2009.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2009.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '51ffa304981d67d069e95255725fe094'
'daymet_ws_2010.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2010.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'e5e4c4445bdbc1fd7628e3ff1c879362'
'daymet_ws_2011.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2011.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '232ced872c7c2d0435d0a3b57231ac0b'
'daymet_ws_2012.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2012.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' 'bf11901ea634ed959898cf308e367ff1'
'daymet_ws_2013.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2013.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '78ce1fb368f0b61f845d96a1de984af7'
'daymet_ws_2014.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2014.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '4cdb76995a6484f69c0e15f264baf9ba'
'daymet_ws_2015.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2015.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '9ce51acdb24bfab878a494aba661729d'
'daymet_ws_2016.nc' 'https://www.earthsystemgrid.org/api/v1/dataset/ucar.ral.hydro.predictions.alaska.vic.daily/file/daymet_ws_2016.nc?api-token=riRefqB3Vxzx7XhAOeNs1s1CMNl2bTHa21eqt9IM' 'md5' '0407f27f23b2dc40844e4a911275e48d'
EOF--dataset.file.url.chksum_type.chksum

}


#
# MAIN
#
echo "Running $(basename $0) version: $version"

#do we have old results? Create the file if not
[ ! -f $CACHE_FILE ] && echo "#filename mtime checksum" > $CACHE_FILE

download

#remove duplicates (if any)
{ rm $CACHE_FILE && tac | awk '!x[$1]++' | tac > $CACHE_FILE; } < $CACHE_FILE