# SATELLITE-IMAGERY-BASED-PROPERTY-VALUATION
This project explores how satellite imagery and structured housing data can be jointly used to improve residential property price prediction. The work begins with exploratory data analysis to understand how price varies with location, property characteristics, and house size. Based on these insights, an XGBoost regression model was developed as the baseline tabular predictor.

To incorporate neighbourhood-level visual information, a ResNet-18-based CNN was trained on satellite images corresponding to each property. The CNN captures spatial cues such as greenery, building density, open land and surrounding layout — signals that are often missing from tabular datasets.

In the final stage, both information sources are brought together using a fusion model. The price predictions from the tabular XGBoost model and the CNN are combined to generate the final estimate. This multimodal setup consistently outperformed either model individually, demonstrating that visual environmental context provides meaningful additional predictive value.

Finally, to improve transparency and interpretability, Grad-CAM visualisation was applied to the CNN predictions as used within the fusion framework. This highlights the image regions contributing most strongly to price estimation, helping to understand how neighbourhood features influence value.

# Dataset Access 
Training data: https://onedrive.live.com/:x:/g/personal/8CF6803ADF7941C3/IQBue1q4w4TETL_7xWMGhcD_AejALtdsXTBejVUjRA9qeM8

Test data: https://onedrive.live.com/:x:/g/personal/8CF6803ADF7941C3/IQAwCVfSggmjQ4DJH51zJK-tARwRQWE9fl0bPlwo1mRF2PQ
# Structure 

├── data/
│   ├── train.csv
│   ├── test.csv
│   └── images/
│       ├── train/
│       └── test/
