# Homography Demo

This is a small Python application that demonstrates perspective transformations (homography) in real-time using OpenCV.

## What it does

The application displays twenty-four overlapping, semi-transparent rectangles. You can click and drag any corner point of these rectangles. When you move a point, a perspective transformation is calculated from the original shape of the rectangle to its new, distorted shape. This transformation is then applied to the entire group of rectangles, warping the whole shape in real-time.

This demonstrates how a homography matrix can map a quadrilateral to another and transform other points in the same plane accordingly.

## How to Use

- Drag a vertex to see the transformation in real-time.
- The **dragged vertex** will appear red.
- The other three vertices of the **same rectangle** will turn blue to indicate which shape is driving the transformation.
- Press **q** to quit the application.

---

# Installation and Usage (macOS)

## 1. Setup Virtual Environment

It is recommended to run this script in a Python virtual environment. Open your terminal and navigate to the project directory.

Create the virtual environment:
```sh
python3 -m venv venv
```

Activate it:
```sh
source venv/bin/activate
```

## 2. Install Dependencies

Install the required Python packages using the `requirements.txt` file:
```sh
pip install -r requirements.txt
```

## 3. Run the Script

Execute the main script to start the application:
```sh
python homography_demo.py
```

---
---

# ホモグラフィデモ

これは、OpenCVを使用してリアルタイムで射影変換（ホモグラフィ）を実演する、小さなPythonアプリケーションです。

## アプリケーションの概要

このアプリケーションは、24個の半透明な長方形が重なって表示されます。これらの長方形の角の点をクリック＆ドラッグすることができます。点を移動すると、元の長方形の形状から新しい歪んだ形状への射影変換が計算されます。この変換は、長方形グループ全体に適用され、形状全体がリアルタイムで歪みます。

これにより、ホモグラフィ行列がどのようにして一つの四角形を別の四角形にマッピングし、同じ平面上の他の点をそれに応じて変換するかを実演します。

## 操作方法

-   頂点をドラッグして、リアルタイムで変換結果を確認します。
-   **ドラッグ中の頂点**は赤色で表示されます。
-   **同じ長方形**の他の3つの頂点は青色に変わり、どの形状が変換の基準になっているかを示します。
-   **q**キーを押してアプリケーションを終了します。

---

# インストールと実行方法 (macOS)

## 1. 仮想環境のセットアップ

このスクリプトは、Pythonの仮想環境で実行することをお勧めします。ターミナルを開き、プロジェクトディレクトリに移動してください。

仮想環境を作成します:
```sh
python3 -m venv venv
```

仮想環境を有効化します:
```sh
source venv/bin/activate
```

## 2. 依存関係のインストール

`requirements.txt` ファイルを使用して、必要なPythonパッケージをインストールします:
```sh
pip install -r requirements.txt
```

## 3. スクリプトの実行

メインスクリプトを実行してアプリケーションを起動します:
```sh
python homography_demo.py
```
