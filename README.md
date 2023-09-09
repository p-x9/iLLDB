# iLLDB
LLDB Extension for iOS App Development

<!-- # Badges -->

[![Github issues](https://img.shields.io/github/issues/p-x9/iLLDB)](https://github.com/p-x9/iLLDB/issues)
[![Github forks](https://img.shields.io/github/forks/p-x9/iLLDB)](https://github.com/p-x9/iLLDB/network/members)
[![Github stars](https://img.shields.io/github/stars/p-x9/iLLDB)](https://github.com/p-x9/iLLDB/stargazers)
[![Github top language](https://img.shields.io/github/languages/top/p-x9/iLLDB)](https://github.com/p-x9/iLLDB/)

## Feature
- [Show view hierarchy](#show-ui-hierarchy)
- [Easy operation of UserDefaults](#userdefaults)
- [Show device information](#deviceinfo)
- [Show App information](#app-info)
- [Show file hierarchy](#file-hierarchy)


## Usage

### UI hierarchy
```
(lldb) ui tree -h
usage:  tree
       [-h]
       [-d]
       [-s]
       [--window WINDOW]
       [--view VIEW]
       [--vc VC]
optional arguments:
  -h, --help
    show this help message and exit
  -d, --detail
    Enable detailed mode (default: False)
  -s, --simple
    Enable simpled mode (default: False)
  --window WINDOW
    Specify the target window (default: None)
  --view VIEW
    Specify the target view (default: None)
  --vc VC
    Specify the target viewController (default: None)
```

#### Example
- Show keyWindow hierarchy
    ```sh
    ui tree
    ```
    ![KeyWindow](./resources/keyWindow.png)

    ```sh
    ui tree -s # simple
    ```
    ![KeyWindow](./resources/keyWindow-simple.png)

    ```sh
    ui tree -d # detail
    ```
    ![KeyWindow](./resources/keyWindow-detail.png)

- Show the hierarchy of a specific view
    ```
    ui tree -view {property name of view}
    ```

- Show the hierarchy of a specific viewController
    ```
    ui tree -vc {property name of viewController}
    ```

- Show the hierarchy of a specific window
    ```
    ui tree -window {property name of window}
    ```

### UserDefaults
#### read
```sh
ud --read "key"
```

#### write
```sh
ud --write "key" "value"
```

#### delete
```sh
ud --delete "key"
```

#### read all
```sh
ud --read-all
```

#### delete all
```sh
ud --delete-all
```

### Device Info
Displays device information.
```sh
device info
```
![device info](./resources/device-info.png)

### App Info
Displays App information.
```sh
app info
```
![app info](./resources/app-info.png)

### File hierarchy
```
(lldb) file tree -h
usage:  tree
       [-h]
       [-l]
       [--documents]
       [--tmp TMP]
optional arguments:
  -h, --help
    show this help message and exit
  -l, --library
    library directory (default: False)
  --documents
    documents directory (default: False)
  --tmp TMP
    tmp directory (default: None)
```

#### Example
- Display the contents of the Library directory
    ```sh
    file tree --library
    ```

- Display the contents of the Documents directory
    ```sh
    file tree --documents
    ```

- Display the contents of the tmp directory
    ```sh
    file tree --tmp
    ```

- Display the contents of a specific directory
    ```sh
    file tree {url}
    ```
![file tree](./resources/file-tree.png)

## License
iLLDB is released under the MIT License. See [LICENSE](./LICENSE)
