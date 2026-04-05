"""Top constituent stocks per sector ETF — used for sub-sector treemap."""

SECTOR_CONSTITUENTS: dict[str, list[str]] = {
    "XLF": ["JPM", "BRK-B", "V", "MA", "BAC", "WFC", "GS", "MS", "SPGI", "AXP", "BLK", "C", "MMC", "CB", "SCHW"],
    "XLRE": ["PLD", "AMT", "EQIX", "CCI", "PSA", "O", "WELL", "DLR", "SPG", "VICI", "AVB", "EQR"],
    "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "CRM", "ADBE", "AMD", "CSCO", "ORCL", "ACN", "INTC", "IBM", "INTU", "TXN", "QCOM"],
    "XLY": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "CMG", "MAR", "ORLY"],
    "XLI": ["CAT", "UNP", "HON", "GE", "RTX", "DE", "BA", "LMT", "UPS", "ADP", "MMM", "WM", "EMR", "ITW"],
    "XLB": ["LIN", "APD", "SHW", "ECL", "FCX", "NUE", "NEM", "DD", "DOW", "VMC", "MLM", "PPG"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PXD", "PSX", "VLO", "OXY", "HES", "WMB"],
    "XLU": ["NEE", "SO", "DUK", "CEG", "SRE", "AEP", "D", "EXC", "PCG", "XEL", "WEC", "ED"],
    "XLV": ["UNH", "JNJ", "LLY", "PFE", "ABT", "TMO", "MRK", "ABBV", "DHR", "BMY", "AMGN", "MDT", "ISRG", "GILD"],
    "XLP": ["PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "MDLZ", "CL", "KMB", "GIS", "STZ"],
}
