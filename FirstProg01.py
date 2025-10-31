# hello_world_file.py

def main():
    filename = "Anuhya.txt"

    # Write "Hello, World!" to a file
    with open(filename, "w") as file:
        file.write("Hello, Anuhya!")

    # Read the content back from the file
    with open(filename, "r") as file:
        content = file.read()

    # Display the content
    print(f"File {filename} created successfully with content 'Hello Anuhya'.")


if __name__ == "__main__":
    main()