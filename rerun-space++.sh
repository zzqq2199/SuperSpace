script_dir=$(dirname "$0")
ps -ef|grep python|grep main.py|grep "space++"|awk '{print $2}' | xargs kill -9
cd $script_dir
uv run main.py &
