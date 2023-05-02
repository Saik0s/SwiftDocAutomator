# SwiftDocAutomator

SwiftDocAutomator is a powerful tool that automatically generates documentation comments for your Swift code, following the official Apple and Swift guidelines. It helps you save time and effort by analyzing your code and producing concise, easy-to-understand documentation.

## Features

- Automatically generates documentation comments for Swift functions and properties
- Follows the official Apple and Swift guidelines for documentation
- Supports class and function summaries
- Easy to integrate into your existing workflow

## Installation

To install SwiftDocAutomator, simply clone the repository and install the required dependencies:

```bash
git clone https://github.com/Saik0s/SwiftDocAutomator.git
cd SwiftDocAutomator
pip install -r requirements.txt
```

## Usage

To use SwiftDocAutomator, run the following command:

```bash
python main.py /path/to/your/swift/file.swift
```

This will generate documentation comments for all functions and properties in the specified Swift file, following the official Apple and Swift guidelines.

## Example

Suppose you have the following Swift function:

```swift
internal static func _typeMismatch(at path: [CodingKey], expectation: Any.Type, reality: Any) -> DecodingError {
    let description = "Expected to decode \(expectation) but found \(_typeDescription(of: reality)) instead."
    return .typeMismatch(expectation, Context(codingPath: path, debugDescription: description))
}
```

SwiftDocAutomator will generate the following documentation comment:

```swift
/// Returns a `.typeMismatch` error describing the expected type.
///
/// - parameter path: The path of `CodingKey`s taken to decode a value of this type.
/// - parameter expectation: The type expected to be encountered.
/// - parameter reality: The value that was encountered instead of the expected type.
/// - returns: A `DecodingError` with the appropriate path and debug description.
```

## Contributing

I'm happy to receive any contributions you may have. If you have any suggestions, bug reports, or feature requests, please feel free to open an issue on the GitHub repository. Your feedback is valuable to me and I appreciate any input you can provide.

## License

SwiftDocAutomator is released under the MIT License. See the LICENSE file for more information.
