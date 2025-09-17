#include <algorithm>
#include <cctype>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>

namespace {
std::string collapse_spaces(const std::string& input) {
    std::string result;
    result.reserve(input.size());
    bool previous_space = false;

    for (char ch : input) {
        unsigned char uch = static_cast<unsigned char>(ch);
        if (std::isspace(uch)) {
            if (!previous_space) {
                result.push_back(' ');
                previous_space = true;
            }
        } else {
            previous_space = false;
            result.push_back(ch);
        }
    }

    // trim leading space
    if (!result.empty() && result.front() == ' ') {
        result.erase(result.begin());
    }
    if (!result.empty() && result.back() == ' ') {
        result.pop_back();
    }

    return result;
}

std::string normalize(const std::string& input) {
    std::string filtered;
    filtered.reserve(input.size());

    for (char ch : input) {
        unsigned char uch = static_cast<unsigned char>(ch);
        if (ch == '\n' || ch == '\r' || ch == '\t') {
            filtered.push_back(' ');
            continue;
        }
        if (std::iscntrl(uch)) {
            continue;
        }
        if (ch == '<') {
            filtered.append("〈");
        } else if (ch == '>') {
            filtered.append("〉");
        } else {
            filtered.push_back(ch);
        }
    }

    return collapse_spaces(filtered);
}

std::string truncate_utf8(const std::string& input, std::size_t max_bytes) {
    if (input.size() <= max_bytes) {
        return input;
    }

    std::string result;
    result.reserve(std::min(input.size(), max_bytes));

    for (std::size_t i = 0; i < input.size();) {
        unsigned char ch = static_cast<unsigned char>(input[i]);
        std::size_t char_len = 1;

        if ((ch & 0x80U) == 0U) {
            char_len = 1;
        } else if ((ch & 0xE0U) == 0xC0U) {
            char_len = 2;
        } else if ((ch & 0xF0U) == 0xE0U) {
            char_len = 3;
        } else if ((ch & 0xF8U) == 0xF0U) {
            char_len = 4;
        } else {
            ++i;
            continue;
        }

        if (i + char_len > input.size()) {
            break;
        }

        if (result.size() + char_len > max_bytes) {
            break;
        }

        result.append(input, i, char_len);
        i += char_len;
    }

    return result;
}

} // namespace

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::string input(
        (std::istreambuf_iterator<char>(std::cin)),
        std::istreambuf_iterator<char>()
    );

    if (input.empty()) {
        return 0;
    }

    std::string normalized = normalize(input);
    std::string truncated = truncate_utf8(normalized, 500U);

    std::cout << truncated;
    return 0;
}
