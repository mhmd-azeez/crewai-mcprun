# Hash Analysis Report

## Test String 1: "password123"

- **MD5:** `482c811da5d5b4bc6d497ffa98491e38`
- **SHA-1:** `cbfdac6008f9cab4083784cbd1874f76618d2a97`
- **SHA-256:** `ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f`

### Analysis
- **MD5**: Quick and suitable for checksums, but vulnerable to collision attacks.
- **SHA-1**: More secure than MD5 but considered insecure for cryptographic functions.
- **SHA-256**: The most secure and recommended for passwords and sensitive data.

### Recommendation
For this common password, **SHA-256** is the recommended hash function due to its strength and security features.

---

## Test String 2: "¡Hola, 世界!"

- **MD5:** `029e893cabb6f404faebcab1a2722603`
- **SHA-1:** `5e32aab97cf8ccb66ce98cfdf09bd9f50536e760`
- **SHA-256:** `fd72ef56ed41d91ec4f9730050f1352bc769d9ddfb4417ef58ff9c01dfa33dd1`

### Analysis
- **MD5 & SHA-1**: Both handle Unicode characters but offer insufficient security.
- **SHA-256**: Maintains integrity across diverse input types and provides stronger security.

### Recommendation
Due to handling of international text and ensuring data security, **SHA-256** is preferred.

---

## Test String 3: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae vestibulum vestibulum."

- **MD5:** `d276276ffa439abe7dc034e774a74aab`
- **SHA-1:** `2cac1d10a65b82a72fb816db2b5fa4c86c0b7f0a`
- **SHA-256:** `b2c66c3e6db87fa889ad9ff2f7a1d1789587b4a8e731dcf739705747da31f686`

### Analysis
- **MD5**: Short and fast but prone to vulnerabilities in long inputs.
- **SHA-1**: Handles longer texts but not suitable for secure applications.
- **SHA-256**: Ideal for long and complex data, offering robust security.

### Recommendation
Use **SHA-256** for handling longer strings given its superior security properties.

---

Overall, due to enhanced security and widespread acceptance, **SHA-256** is the recommended hashing algorithm for most applications, especially when dealing with sensitive information or diverse character sets.