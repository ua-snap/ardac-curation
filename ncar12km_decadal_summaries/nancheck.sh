for file in $(find . -name "*.csv"); do
    if grep -q 'nan' "$file"; then
        echo "In file $file:"
        grep -n -w 'nan' "$file"
        echo ""
    fi
done
exit 0
