//+------------------------------------------------------------------+
//|                                           GridHedgeGold_EA.mq5   |
//|                                        Grid + Hedge Strategy     |
//|                                        For Gold (XAUUSD)         |
//+------------------------------------------------------------------+
#property copyright "Grid Hedge Strategy"
#property link      ""
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>

//--- Input parameters
input group "=== Capital Settings ==="
input double   InpInitialCapital = 10000.0;  // Initial Capital (USD)
input double   InpRiskPercent = 2.0;          // Risk per trade (%)

input group "=== Grid Settings ==="
input double   InpGridStep = 1.6;             // Grid step (%)
input double   InpTakeProfit = 2.4;           // Take profit (%)
input int      InpMaxGridLevels = 10;         // Max grid levels
input double   InpGridSizePercent = 3.0;      // Grid position size (% of capital)

input group "=== Hedge Settings ==="
input bool     InpEnableHedge = true;         // Enable hedge
input double   InpHedgeTriggerATR = 2.5;      // Hedge trigger (ATR multiplier)
input double   InpHedgeSizePercent = 15.0;    // Hedge size (% of capital)
input int      InpHedgeLeverage = 2;          // Hedge leverage

input group "=== Indicators ==="
input int      InpEMAPeriod = 50;             // EMA Period
input int      InpATRPeriod = 14;             // ATR Period

input group "=== Risk Management ==="
input double   InpMaxDrawdown = 29.0;         // Max drawdown (%)
input double   InpMaxSpread = 0.5;            // Max spread (USD)

input group "=== Order Settings ==="
input int      InpMagicNumber = 123456;       // Magic number
input string   InpCommentGrid = "GRID";       // Grid order comment
input string   InpCommentHedge = "HEDGE";     // Hedge order comment

//--- Global variables
CTrade         trade;
CPositionInfo  position;

int            handleEMA;
int            handleATR;
double         emaBuffer[];
double         atrBuffer[];

double         centerPrice = 0.0;
double         peakEquity = 0.0;
datetime       lastFundingTime = 0;

struct GridLevel {
   double price;
   double lots;
   ulong  ticket;
   bool   active;
};

GridLevel      gridLevels[];
int            gridCount = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=== Grid + Hedge EA Initializing ===");
   
   //--- Set up trade
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(10);
   trade.SetTypeFilling(ORDER_FILLING_FOK);
   trade.SetAsyncMode(false);
   
   //--- Initialize indicators
   handleEMA = iMA(_Symbol, PERIOD_H1, InpEMAPeriod, 0, MODE_EMA, PRICE_CLOSE);
   handleATR = iATR(_Symbol, PERIOD_H1, InpATRPeriod);
   
   if(handleEMA == INVALID_HANDLE || handleATR == INVALID_HANDLE) {
      Print("ERROR: Failed to create indicators!");
      return INIT_FAILED;
   }
   
   ArraySetAsSeries(emaBuffer, true);
   ArraySetAsSeries(atrBuffer, true);
   
   //--- Initialize grid
   ArrayResize(gridLevels, InpMaxGridLevels);
   for(int i = 0; i < InpMaxGridLevels; i++) {
      gridLevels[i].active = false;
      gridLevels[i].ticket = 0;
   }
   
   //--- Initialize capital tracking
   peakEquity = InpInitialCapital;
   
   Print("EA initialized successfully");
   Print("Symbol: ", _Symbol);
   Print("Initial Capital: $", InpInitialCapital);
   Print("Grid Step: ", InpGridStep, "%");
   Print("Take Profit: ", InpTakeProfit, "%");
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("=== EA Deinitialization ===");
   
   //--- Release indicators
   if(handleEMA != INVALID_HANDLE) IndicatorRelease(handleEMA);
   if(handleATR != INVALID_HANDLE) IndicatorRelease(handleATR);
   
   Print("EA stopped. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   //--- Check if new bar
   static datetime lastBar = 0;
   datetime currentBar = iTime(_Symbol, PERIOD_H1, 0);
   if(currentBar == lastBar) return;
   lastBar = currentBar;
   
   //--- Update indicators
   if(!UpdateIndicators()) return;
   
   //--- Get current price and values
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = ask - bid;
   
   //--- Check spread
   if(spread > InpMaxSpread) {
      Print("Spread too high: ", spread, " > ", InpMaxSpread);
      return;
   }
   
   double currentEMA = emaBuffer[0];
   double currentATR = atrBuffer[0];
   
   //--- Update center price
   if(centerPrice == 0) centerPrice = currentEMA;
   
   //--- Check drawdown
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(currentEquity > peakEquity) peakEquity = currentEquity;
   
   double drawdown = (peakEquity - currentEquity) / peakEquity * 100.0;
   if(drawdown > InpMaxDrawdown) {
      Print("WARNING: Max drawdown reached: ", drawdown, "%");
      CloseAllPositions();
      return;
   }
   
   //--- Rebalance grid center
   RebalanceGrid(currentEMA);
   
   //--- Execute grid logic
   GridBuyLogic(bid, currentEMA);
   GridSellLogic(ask, currentEMA);
   
   //--- Execute hedge logic
   if(InpEnableHedge) {
      HedgeLogic(bid, currentEMA, currentATR);
   }
   
   //--- Apply funding rate (every 8 hours)
   ApplyFundingRate();
   
   //--- Display info
   DisplayInfo(currentEMA, currentATR, drawdown);
}

//+------------------------------------------------------------------+
//| Update indicator buffers                                         |
//+------------------------------------------------------------------+
bool UpdateIndicators()
{
   if(CopyBuffer(handleEMA, 0, 0, 3, emaBuffer) < 3) {
      Print("ERROR: Failed to copy EMA buffer");
      return false;
   }
   
   if(CopyBuffer(handleATR, 0, 0, 3, atrBuffer) < 3) {
      Print("ERROR: Failed to copy ATR buffer");
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Rebalance grid around new center                                 |
//+------------------------------------------------------------------+
void RebalanceGrid(double newCenter)
{
   if(MathAbs(newCenter - centerPrice) / centerPrice < 0.005) return; // < 0.5% change
   
   Print("Rebalancing grid: ", centerPrice, " -> ", newCenter);
   centerPrice = newCenter;
   
   //--- Update grid levels without closing positions
   //--- (Positions remain, only level tracking updated)
}

//+------------------------------------------------------------------+
//| Grid buy logic                                                   |
//+------------------------------------------------------------------+
void GridBuyLogic(double price, double ema)
{
   //--- Only buy below EMA
   if(price >= ema) return;
   
   //--- Check if we already have position at this level
   double gridStep = ema * InpGridStep / 100.0;
   int level = (int)((ema - price) / gridStep);
   
   if(level < 0 || level >= InpMaxGridLevels) return;
   if(gridLevels[level].active) return; // Already bought at this level
   
   //--- Calculate lot size
   double lotSize = CalculateLotSize(InpGridSizePercent);
   if(lotSize <= 0) return;
   
   //--- Open buy order
   if(trade.Buy(lotSize, _Symbol, 0, 0, 0, InpCommentGrid)) {
      ulong ticket = trade.ResultOrder();
      gridLevels[level].price = price;
      gridLevels[level].lots = lotSize;
      gridLevels[level].ticket = ticket;
      gridLevels[level].active = true;
      gridCount++;
      
      Print("GRID BUY: Level ", level, " | Price: ", price, " | Lots: ", lotSize);
   }
}

//+------------------------------------------------------------------+
//| Grid sell logic (take profit)                                    |
//+------------------------------------------------------------------+
void GridSellLogic(double price, double ema)
{
   //--- Check each active grid level for take profit
   for(int i = 0; i < InpMaxGridLevels; i++) {
      if(!gridLevels[i].active) continue;
      
      double entryPrice = gridLevels[i].price;
      double takeProfitPrice = entryPrice * (1 + InpTakeProfit / 100.0);
      
      //--- Check if price reached take profit
      if(price >= takeProfitPrice) {
         //--- Close position
         if(ClosePositionByTicket(gridLevels[i].ticket)) {
            Print("GRID SELL: Level ", i, " | Entry: ", entryPrice, " | Exit: ", price, 
                  " | Profit: ", (price - entryPrice) * gridLevels[i].lots);
            
            gridLevels[i].active = false;
            gridLevels[i].ticket = 0;
            gridCount--;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Hedge logic                                                      |
//+------------------------------------------------------------------+
void HedgeLogic(double price, double ema, double atr)
{
   if(atr == 0 || ema == 0) return;
   
   double distance = MathAbs(price - ema);
   double atrDistance = distance / atr;
   
   //--- Open hedge if price too far from EMA (downside protection)
   if(atrDistance > InpHedgeTriggerATR && price < ema) {
      if(!HasHedgePosition()) {
         double lotSize = CalculateLotSize(InpHedgeSizePercent) * InpHedgeLeverage;
         
         if(trade.Sell(lotSize, _Symbol, 0, 0, 0, InpCommentHedge)) {
            Print("HEDGE OPEN: Price far from EMA | Distance: ", atrDistance, " ATR | Lots: ", lotSize);
         }
      }
   }
   
   //--- Close hedge if price returns near EMA
   if(atrDistance < InpHedgeTriggerATR * 0.5) {
      if(HasHedgePosition()) {
         CloseHedgePositions();
         Print("HEDGE CLOSE: Price returned to EMA");
      }
   }
}

//+------------------------------------------------------------------+
//| Calculate lot size based on capital percentage                   |
//+------------------------------------------------------------------+
double CalculateLotSize(double capitalPercent)
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double positionValue = equity * capitalPercent / 100.0;
   
   double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double contractSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   
   double lots = positionValue / (price * contractSize);
   
   //--- Normalize lot size
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   
   lots = MathFloor(lots / lotStep) * lotStep;
   lots = MathMax(lots, minLot);
   lots = MathMin(lots, maxLot);
   
   return lots;
}

//+------------------------------------------------------------------+
//| Check if hedge position exists                                   |
//+------------------------------------------------------------------+
bool HasHedgePosition()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(position.SelectByIndex(i)) {
         if(position.Symbol() == _Symbol && 
            position.Magic() == InpMagicNumber &&
            StringFind(position.Comment(), InpCommentHedge) >= 0 &&
            position.PositionType() == POSITION_TYPE_SELL) {
            return true;
         }
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Close hedge positions                                            |
//+------------------------------------------------------------------+
void CloseHedgePositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(position.SelectByIndex(i)) {
         if(position.Symbol() == _Symbol && 
            position.Magic() == InpMagicNumber &&
            StringFind(position.Comment(), InpCommentHedge) >= 0) {
            trade.PositionClose(position.Ticket());
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Close position by ticket                                         |
//+------------------------------------------------------------------+
bool ClosePositionByTicket(ulong ticket)
{
   if(ticket == 0) return false;
   
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(position.SelectByIndex(i)) {
         if(position.Ticket() == ticket) {
            return trade.PositionClose(ticket);
         }
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Close all positions                                              |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   Print("EMERGENCY: Closing all positions!");
   
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(position.SelectByIndex(i)) {
         if(position.Symbol() == _Symbol && position.Magic() == InpMagicNumber) {
            trade.PositionClose(position.Ticket());
         }
      }
   }
   
   //--- Reset grid
   for(int i = 0; i < InpMaxGridLevels; i++) {
      gridLevels[i].active = false;
      gridLevels[i].ticket = 0;
   }
   gridCount = 0;
}

//+------------------------------------------------------------------+
//| Apply funding rate (simulated for MT5)                           |
//+------------------------------------------------------------------+
void ApplyFundingRate()
{
   datetime currentTime = TimeCurrent();
   
   //--- Check if 8 hours passed
   if(lastFundingTime == 0) {
      lastFundingTime = currentTime;
      return;
   }
   
   int hoursPassed = (int)((currentTime - lastFundingTime) / 3600);
   if(hoursPassed >= 8) {
      //--- Apply small funding cost on hedge positions (0.01% per 8h)
      double fundingRate = 0.0001;
      
      for(int i = PositionsTotal() - 1; i >= 0; i--) {
         if(position.SelectByIndex(i)) {
            if(position.Symbol() == _Symbol && 
               position.Magic() == InpMagicNumber &&
               StringFind(position.Comment(), InpCommentHedge) >= 0) {
               
               double cost = position.Volume() * position.PriceOpen() * fundingRate;
               Print("Funding cost applied: $", cost);
            }
         }
      }
      
      lastFundingTime = currentTime;
   }
}

//+------------------------------------------------------------------+
//| Display info on chart                                            |
//+------------------------------------------------------------------+
void DisplayInfo(double ema, double atr, double drawdown)
{
   string info = "\n";
   info += "=== GRID + HEDGE STRATEGY ===\n";
   info += "Symbol: " + _Symbol + "\n";
   info += "EMA50: " + DoubleToString(ema, 2) + "\n";
   info += "ATR: " + DoubleToString(atr, 2) + "\n";
   info += "---\n";
   info += "Equity: $" + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2) + "\n";
   info += "Drawdown: " + DoubleToString(drawdown, 2) + "%\n";
   info += "---\n";
   info += "Grid Levels: " + IntegerToString(gridCount) + "/" + IntegerToString(InpMaxGridLevels) + "\n";
   info += "Hedge: " + (HasHedgePosition() ? "ACTIVE" : "INACTIVE") + "\n";
   info += "Total Positions: " + IntegerToString(PositionsTotal()) + "\n";
   
   Comment(info);
}

//+------------------------------------------------------------------+
