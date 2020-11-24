// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.8.0;

/**
 * @dev Standard math utilities missing in the Solidity language.
 */

// 创建了 供调用的数学工具库
library Math {
    /**
     * @dev Returns the largest of two numbers.
     */
    // max 返回两个int 的最大值， 使用uint256 最大的uint，防止异常
    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a >= b ? a : b;
    }

    /**
     * @dev Returns the smallest of two numbers.
     */
    // min 返回两个int 的最小值，使用uint256
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }

    /**
     * @dev Returns the average of two numbers. The result is rounded towards
     * zero.
     */
    // average 返回两个int 的算数平均数，为了防止溢出的情况，使用了(a / 2) + (b / 2) + ((a % 2 + b % 2) / 2)的算法，保证不会溢出，并返回了正确的算术平均数
    function average(uint256 a, uint256 b) internal pure returns (uint256) {
        // (a + b) / 2 can overflow, so we distribute
        return (a / 2) + (b / 2) + ((a % 2 + b % 2) / 2);
    }
}
