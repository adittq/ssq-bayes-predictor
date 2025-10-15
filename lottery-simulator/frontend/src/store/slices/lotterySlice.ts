import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { lotteryAPI } from '../../services/api';

export interface LotteryDraw {
  id: number;
  period: string;
  red_balls: number[];
  blue_ball: number;
  draw_date: string;
  total_sales: number;
  prize_pool: number;
}

export interface Purchase {
  id: number;
  period: string;
  red_balls: number[];
  blue_ball: number;
  multiple: number;
  bet_amount: number;
  total_amount: number;
  purchase_time: string;
  status: string;
}

export interface PrizeLevel {
  level: number;
  name: string;
  condition: string;
  base_prize: number;
}

export interface LotteryState {
  currentPeriod: {
    period: string;
    draw_date: string;
    is_drawn: boolean;
    sales_deadline: string;
    can_purchase: boolean;
  } | null;
  historicalDraws: LotteryDraw[];
  purchases: Purchase[];
  prizeLevels: PrizeLevel[];
  quickPickNumbers: {
    red_balls: number[];
    blue_ball: number;
  } | null;
  statistics: {
    total_purchases: number;
    total_amount: number;
    total_winnings: number;
    win_rate: number;
  } | null;
  loading: boolean;
  error: string | null;
}

const initialState: LotteryState = {
  currentPeriod: null,
  historicalDraws: [],
  purchases: [],
  prizeLevels: [],
  quickPickNumbers: null,
  statistics: null,
  loading: false,
  error: null,
};

// 获取当前期号
export const getCurrentPeriod = createAsyncThunk(
  'lottery/getCurrentPeriod',
  async (_, { rejectWithValue }) => {
    try {
      const response = await lotteryAPI.getCurrentPeriod();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取当前期号失败');
    }
  }
);

// 获取历史开奖
export const getHistoricalDraws = createAsyncThunk(
  'lottery/getHistoricalDraws',
  async (limit: number = 50, { rejectWithValue }) => {
    try {
      const response = await lotteryAPI.getHistoricalDraws(limit);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取历史开奖失败');
    }
  }
);

// 快速选号
export const quickPick = createAsyncThunk(
  'lottery/quickPick',
  async (_, { rejectWithValue }) => {
    try {
      const response = await lotteryAPI.quickPick();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '快速选号失败');
    }
  }
);

// 购买彩票
export const purchaseLottery = createAsyncThunk(
  'lottery/purchase',
  async (data: {
    red_balls: number[];
    blue_ball: number;
    multiple: number;
    period?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await lotteryAPI.purchase(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '购买失败');
    }
  }
);

// 批量购买
export const batchPurchase = createAsyncThunk(
  'lottery/batchPurchase',
  async (data: {
    purchases: Array<{
      red_balls: number[];
      blue_ball: number;
      multiple: number;
    }>;
    period?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await lotteryAPI.batchPurchase(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '批量购买失败');
    }
  }
);

// 获取购买历史
export const getPurchaseHistory = createAsyncThunk(
  'lottery/getPurchaseHistory',
  async (params: {
    period?: string;
    page?: number;
    size?: number;
  }, { rejectWithValue }) => {
    try {
      const response = await lotteryAPI.getPurchaseHistory(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取购买历史失败');
    }
  }
);

// 获取购买统计
export const getPurchaseStatistics = createAsyncThunk(
  'lottery/getPurchaseStatistics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await lotteryAPI.getPurchaseStatistics();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取购买统计失败');
    }
  }
);

// 获取奖级信息
export const getPrizeLevels = createAsyncThunk(
  'lottery/getPrizeLevels',
  async (_, { rejectWithValue }) => {
    try {
      const response = await lotteryAPI.getPrizeLevels();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取奖级信息失败');
    }
  }
);

const lotterySlice = createSlice({
  name: 'lottery',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearQuickPick: (state) => {
      state.quickPickNumbers = null;
    },
    setSelectedNumbers: (state, action: PayloadAction<{
      red_balls: number[];
      blue_ball: number;
    }>) => {
      state.quickPickNumbers = action.payload;
    },
  },
  extraReducers: (builder) => {
    // 获取当前期号
    builder
      .addCase(getCurrentPeriod.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getCurrentPeriod.fulfilled, (state, action) => {
        state.loading = false;
        state.currentPeriod = action.payload;
      })
      .addCase(getCurrentPeriod.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 获取历史开奖
    builder
      .addCase(getHistoricalDraws.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getHistoricalDraws.fulfilled, (state, action) => {
        state.loading = false;
        state.historicalDraws = action.payload;
      })
      .addCase(getHistoricalDraws.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 快速选号
    builder
      .addCase(quickPick.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(quickPick.fulfilled, (state, action) => {
        state.loading = false;
        state.quickPickNumbers = action.payload;
      })
      .addCase(quickPick.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 购买彩票
    builder
      .addCase(purchaseLottery.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(purchaseLottery.fulfilled, (state, action) => {
        state.loading = false;
        state.purchases.unshift(action.payload);
      })
      .addCase(purchaseLottery.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 批量购买
    builder
      .addCase(batchPurchase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(batchPurchase.fulfilled, (state, action) => {
        state.loading = false;
        state.purchases = [...action.payload, ...state.purchases];
      })
      .addCase(batchPurchase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 获取购买历史
    builder
      .addCase(getPurchaseHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getPurchaseHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.purchases = action.payload.purchases;
      })
      .addCase(getPurchaseHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 获取购买统计
    builder
      .addCase(getPurchaseStatistics.fulfilled, (state, action) => {
        state.statistics = action.payload;
      });

    // 获取奖级信息
    builder
      .addCase(getPrizeLevels.fulfilled, (state, action) => {
        state.prizeLevels = action.payload;
      });
  },
});

export const { clearError, clearQuickPick, setSelectedNumbers } = lotterySlice.actions;
export default lotterySlice.reducer;