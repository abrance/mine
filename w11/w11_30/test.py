
class Solution:
    def longestPalindrome(self, s: str) -> str:
        max_str = ""
        for i, _str in enumerate(s):
            if i == 0:
                if len(s) == 1:
                    return s
                else:
                    continue
            else:
                _max = self.c(s, i-1, i)
                _max_2 = self.c(s, i-1, i+1)
                # print('{} {}'.format(_max, _max_2))
                _max = _max if len(_max) > len(_max_2) else _max_2
                if len(_max) > len(max_str):
                    max_str = _max
        return max_str

    def c(self, _string, start, end):
        if start >= 0 and end <= len(_string)-1:
            if _string[start] == _string[end]:
                return self.c(_string, start-1, end+1)
            else:
                return "" if end-start <= 1 else _string[start+1: end]
        else:
            return "" if end-start <= 1 else _string[start+1: end]


def test_solution():
    s = Solution()
    _test = "SQQSYYSQQS"
    a = s.longestPalindrome(_test)
    # assert a == 'abccba'
    print(a)


if __name__ == '__main__':
    test_solution()
