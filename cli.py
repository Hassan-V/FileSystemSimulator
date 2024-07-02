import argparse
import os
import traceback
from models import FileSystem

def load_file_system(state_file):
    if os.path.exists(state_file):
        return FileSystem.load_state(state_file)
    return FileSystem()

def save_file_system(fs, state_file):
    fs.save_state(state_file)

def main():
    parser = argparse.ArgumentParser(description="Simple File System Simulator")
    parser.add_argument("action", choices=[
        "create_file", "read_file", "write_file", "delete", 
        "list_dir", "stats", "create_drive", "copy", 
        "move", "rename", "search"
    ], help="Action to perform")
    parser.add_argument("-p", "--path", help="Path for the action", required=False)
    parser.add_argument("-n", "--name", help="Name for file or directory", required=False)
    parser.add_argument("-c", "--content", help="Content for the file", required=False)
    parser.add_argument("-d", "--drive_name", help="Name for the virtual drive", required=False)
    parser.add_argument("-s", "--source", help="Source path for copy or move", required=False)
    parser.add_argument("-t", "--destination", help="Destination path for copy or move", required=False)
    parser.add_argument("-r", "--new_name", help="New name for rename action", required=False)
    parser.add_argument("-q", "--search_term", help="Search term for search action", required=False)
    parser.add_argument("-f", "--state_file", help="State file name", default="fs_state.pkl", required=False)

    args = parser.parse_args()
    fs = load_file_system(args.state_file)

    try:
        if args.action == "create_drive" and args.drive_name:
            fs.create_virtual_drive(args.drive_name)
            print(f"Virtual drive '{args.drive_name}' created.")
        elif args.action == "create_file" and args.path and args.name:
            fs.create_file(args.path, args.name, args.content or "")
            print(f"File '{args.name}' created at '{args.path}'.")
        elif args.action == "read_file" and args.path:
            content = fs.read_file(args.path)
            print(f"Content of '{args.path}':\n{content}")
        elif args.action == "write_file" and args.path and args.content:
            fs.write_file(args.path, args.content)
            print(f"File at '{args.path}' updated.")
        elif args.action == "delete" and args.path:
            fs.delete(args.path)
            print(f"Deleted '{args.path}'.")
        elif args.action == "list_dir":
            path = args.path or "/"
            contents = fs.list_dir(path)
            print(f"Contents of '{path}':\n{contents}")
        elif args.action == "stats":
            stats = fs.statistics()
            print(f"File System Statistics:\nTotal Files: {stats['total_files']}\nTotal Directories: {stats['total_directories']}\nTotal Size: {stats['total_size']} bytes")
        elif args.action == "copy" and args.source and args.destination:
            fs.copy(args.source, args.destination)
            print(f"Copied from '{args.source}' to '{args.destination}'.")
        elif args.action == "move" and args.source and args.destination:
            fs.move(args.source, args.destination)
            print(f"Moved from '{args.source}' to '{args.destination}'.")
        elif args.action == "rename" and args.path and args.new_name:
            fs.rename(args.path, args.new_name)
            print(f"Renamed '{args.path}' to '{args.new_name}'.")
        elif args.action == "search" and args.path and args.search_term:
            results = fs.search(args.path, args.search_term)
            print(f"Search results for '{args.search_term}':\n{results}")
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

    save_file_system(fs, args.state_file)

if __name__ == "__main__":
    main()
