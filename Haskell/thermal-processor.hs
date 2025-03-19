-- ThermalProcessorBinary.hs
{-# LANGUAGE OverloadedStrings #-}

import Control.Monad (forever, replicateM) -- 添加此导入
import Data.Binary.Get
import qualified Data.ByteString as B
import qualified Data.ByteString.Lazy as BL
import System.IO (BufferMode (..), hSetBuffering, stdin)

-- 数据解析函数保持不变
parseThermalData :: Get (Double, [Float])
parseThermalData = do
    timestamp <- getDoublele
    temperatures <- replicateM 768 getFloatle -- 现在 replicateM 已可用
    return (timestamp, temperatures)

arrayToMatrix_32 :: [Float] -> [[Float]]
arrayToMatrix_32 [] = []
arrayToMatrix_32 (xs) = take 32 (xs) : arrayToMatrix_32 (drop 32 xs)

normalize :: [Float] -> [Float] -- 温度数据归一函数
normalize [] = []
normalize (x : xs)
    | x <= 10 = 0 : normalize xs
    | x <= 40 = ((x - 10) / 30) : normalize xs -- 主要监控10-40度
    | otherwise = 1 : normalize xs

jetColor :: Float -> (Int, Int, Int) -- 温度数据映射至RGB
jetColor x = (round (clamp r * 255), round (clamp g * 255), round (clamp b * 255))
  where
    -- 分段计算RGB分量
    (r, g, b)
        | x < 0.125 = (0, 0, 0.5 + 4 * x) -- 深蓝到蓝
        | x < 0.375 = (0, 4 * (x - 0.125), 1.0) -- 蓝到青
        | x < 0.625 = (4 * (x - 0.375), 1.0, 1.0 - 4 * (x - 0.375)) -- 青到黄
        | x < 0.875 = (1.0, 1.0 - 4 * (x - 0.625), 0) -- 黄到红
        | x <= 1 = (max (1.0 - 4 * (x - 0.875)) 0.5, 0, 0) -- 红到暗红
        | otherwise = (1, 1, 1) -- 将特殊值映射成白色
    clamp = max 0 . min 1

scaleMatrix :: Int -> [[(Int,Int,Int)]] -> [[(Int,Int,Int)]]
scaleMatrix factor = concatMap (replicate factor) . map (concatMap (replicate factor)) -- 不全调用

tempRecogAlgo :: [[Int]] -> [[Int]] -- 危险温度矩阵转换图像识别
tempRecogAlgo [] = []
tempRecogAlgo (x : xs) = tempRecogAlgo_step2 x : tempRecogAlgo xs -- 脱一层外壳
  where
    tempRecogAlgo_step2 ys = map (\n -> encircleAlgo ys n) [1 .. 30]
      where
        encircleAlgo ys n
            | n - 1 == 0 && ys !! (n - 1) /= 0 = 3 -- 边界包围
            | n + 1 == 31 && ys !! (n + 1) /= 0 = 3 -- 边界包围
            | ys !! n == ys !! (n - 1) && ys !! n < ys !! (n + 1) = 3 -- 002
            | ys !! n == ys !! (n - 1) && ys !! n == ys !! (n + 1) = ys !! n -- 222/000
            | ys !! n < ys !! (n - 1) && ys !! n == ys !! (n + 1) = 3 -- 200
            | ys !! n > ys !! (n - 1) && ys !! n == ys !! (n + 1) = ys !! n -- 022
            | ys !! n == ys !! (n - 1) && ys !! n > ys !! (n + 1) = ys !! n -- 220
            | otherwise = ys !! n

filterUselessWarning :: [[Int]] -> [[Int]]
filterUselessWarning [] = []
filterUselessWarning (x : xs) = filterUselessWarning_step2 x : filterUselessWarning xs
  where
    filterUselessWarning_step2 (y : ys) =
        if y /= 3
            then 0 : filterUselessWarning_step2 ys
            else 3 : filterUselessWarning_step2 ys

{- 变换模式 temp :: [Float] -> maxTemp :: Float
                            -> minTemp :: Float
                            ->
-}
main :: IO ()
main = do
    hSetBuffering stdin NoBuffering
    let chunkSize = 8 + 4 * 768

    forever $ do
        bytes <- B.hGet stdin chunkSize
        case runGetOrFail parseThermalData (BL.fromStrict bytes) of
            Left (_, _, err) ->
                putStrLn $ "解析错误: " ++ err
            Right (_, _, (ts, temps)) -> do
                let maxTemp = maximum temps -- 求最大温度
                let minTemp = minimum temps
                let tempNormalization = normalize temps -- 将温度数据归一至0-1
                let tempNormalizationMatrix = arrayToMatrix_32 tempNormalization -- 将768个归一化的温度数据存进32*24的二维矩阵
                let tempColorMap = refillMatrixWithColor tempNormalizationMatrix where -- 将归一化的矩阵数据转为RGB矩阵
                    refillMatrixWithColor [] = []
                    refillMatrixWithColor (x : xs) = refillArrayWithColor x : refillMatrixWithColor xs
                      where
                        refillArrayWithColor [] = []
                        refillArrayWithColor (y : ys) = jetColor y : refillArrayWithColor ys
                let scaledTempColorMap = scaleMatrix 10 tempColorMap -- 76800个rgb矩阵
                -- 基本图像处理完成
                let warningTempMatrix = refillMatrixWithTemp tempNormalizationMatrix where -- 过滤32*24矩阵，记录危险温度
                    refillMatrixWithTemp [] = []
                    refillMatrixWithTemp (x : xs) = refillArrayWithTemp x : refillMatrixWithTemp xs -- 脱一层外壳
                      where
                        refillArrayWithTemp [] = []
                        refillArrayWithTemp (y : ys)
                            | y < 1 / 3 = 0 : refillArrayWithTemp ys -- 小于30度
                            | y < 1 = 1 : refillArrayWithTemp ys -- 小于40度 为测试方便，将1、2全部当成危险温度识别
                            | otherwise = 2 : refillArrayWithTemp ys -- 大于等于40度
                let recogRectangle = tempRecogAlgo warningTempMatrix
                let filteredRecogRectangle = filterUselessWarning recogRectangle
                putStrLn $ "时间戳: " ++ show ts
                putStrLn $ "最高温度: " ++ show maxTemp ++ "°C"
                -- putStrLn $ "所有温度热力图: " ++ show tempColorMap
                putStrLn $ "警告温度: " ++ show recogRectangle
                putStrLn "--------------------------"
