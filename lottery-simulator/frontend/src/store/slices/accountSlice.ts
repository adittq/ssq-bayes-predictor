import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { accountAPI } from '../../services/api';

export interface Transaction {
  id: number;
  type: string;
  amount: number;
  balance_before: number;
  balance_after: number;
  description: string;
  transaction_time: string;
}

export interface AccountBalance {
  balance: number;
  frozen_amount: number;
  available_balance: number;
  total_recharge: number;
  total_consumption: number;
  total_winnings: number;
  daily_limit: number;
  monthly_limit: number;
  created_at: string;
}

export interface AccountStatistics {
  current_balance: number;
  frozen_amount: number;
  available_balance: number;
  total_recharge: number;
  total_consumption: number;
  total_winnings: number;
  monthly_stats: {
    recharge: number;
    consumption: number;
    winnings: number;
    net_change: number;
  };
  daily_stats: {
    consumption: number;
    remaining_daily_limit: number;
  };
  limits: {
    daily_limit: number;
    monthly_limit: number;
  };
}

export interface AccountState {
  balance: AccountBalance | null;
  transactions: Transaction[];
  statistics: AccountStatistics | null;
  balanceHistory: Array<{
    date: string;
    time: string;
    balance: number;
    change: number;
    type: string;
    description: string;
  }>;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    size: number;
    total: number;
    pages: number;
  } | null;
}

const initialState: AccountState = {
  balance: null,
  transactions: [],
  statistics: null,
  balanceHistory: [],
  loading: false,
  error: null,
  pagination: null,
};

// 获取账户余额
export const getAccountBalance = createAsyncThunk(
  'account/getBalance',
  async (_, { rejectWithValue }) => {
    try {
      const response = await accountAPI.getBalance();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取账户余额失败');
    }
  }
);

// 充值
export const recharge = createAsyncThunk(
  'account/recharge',
  async (data: { amount: number; payment_method: string }, { rejectWithValue }) => {
    try {
      const response = await accountAPI.recharge(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '充值失败');
    }
  }
);

// 提现
export const withdraw = createAsyncThunk(
  'account/withdraw',
  async (data: { amount: number; payment_method: string }, { rejectWithValue }) => {
    try {
      const response = await accountAPI.withdraw(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '提现失败');
    }
  }
);

// 获取交易历史
export const getTransactionHistory = createAsyncThunk(
  'account/getTransactionHistory',
  async (params: {
    transaction_type?: string;
    page?: number;
    size?: number;
    start_date?: string;
    end_date?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await accountAPI.getTransactionHistory(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取交易历史失败');
    }
  }
);

// 获取账户统计
export const getAccountStatistics = createAsyncThunk(
  'account/getStatistics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await accountAPI.getAccountStatistics();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取账户统计失败');
    }
  }
);

// 设置账户限额
export const setAccountLimits = createAsyncThunk(
  'account/setLimits',
  async (data: {
    daily_limit?: number;
    monthly_limit?: number;
  }, { rejectWithValue }) => {
    try {
      const response = await accountAPI.setAccountLimits(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '设置限额失败');
    }
  }
);

// 获取余额历史
export const getBalanceHistory = createAsyncThunk(
  'account/getBalanceHistory',
  async (days: number = 30, { rejectWithValue }) => {
    try {
      const response = await accountAPI.getBalanceHistory(days);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取余额历史失败');
    }
  }
);

const accountSlice = createSlice({
  name: 'account',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    updateBalance: (state, action: PayloadAction<number>) => {
      if (state.balance) {
        state.balance.balance = action.payload;
        state.balance.available_balance = action.payload - state.balance.frozen_amount;
      }
    },
    addTransaction: (state, action: PayloadAction<Transaction>) => {
      state.transactions.unshift(action.payload);
    },
  },
  extraReducers: (builder) => {
    // 获取账户余额
    builder
      .addCase(getAccountBalance.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getAccountBalance.fulfilled, (state, action) => {
        state.loading = false;
        state.balance = action.payload;
      })
      .addCase(getAccountBalance.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 充值
    builder
      .addCase(recharge.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(recharge.fulfilled, (state, action) => {
        state.loading = false;
        // 更新余额
        if (state.balance) {
          state.balance.balance = action.payload.balance_after;
          state.balance.available_balance = action.payload.balance_after - state.balance.frozen_amount;
          state.balance.total_recharge += action.payload.amount;
        }
        // 添加交易记录
        const transaction: Transaction = {
          id: action.payload.transaction_id,
          type: 'recharge',
          amount: action.payload.amount,
          balance_before: action.payload.balance_before,
          balance_after: action.payload.balance_after,
          description: `账户充值 - ${action.payload.payment_method}`,
          transaction_time: action.payload.transaction_time,
        };
        state.transactions.unshift(transaction);
      })
      .addCase(recharge.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 提现
    builder
      .addCase(withdraw.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(withdraw.fulfilled, (state, action) => {
        state.loading = false;
        // 更新余额
        if (state.balance) {
          state.balance.balance = action.payload.balance_after;
          state.balance.available_balance = action.payload.balance_after - state.balance.frozen_amount;
        }
        // 添加交易记录
        const transaction: Transaction = {
          id: action.payload.transaction_id,
          type: 'withdraw',
          amount: action.payload.amount,
          balance_before: action.payload.balance_before,
          balance_after: action.payload.balance_after,
          description: `账户提现 - ${action.payload.payment_method}`,
          transaction_time: action.payload.transaction_time,
        };
        state.transactions.unshift(transaction);
      })
      .addCase(withdraw.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 获取交易历史
    builder
      .addCase(getTransactionHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getTransactionHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.transactions = action.payload.transactions;
        state.pagination = action.payload.pagination;
      })
      .addCase(getTransactionHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 获取账户统计
    builder
      .addCase(getAccountStatistics.fulfilled, (state, action) => {
        state.statistics = action.payload;
      });

    // 设置账户限额
    builder
      .addCase(setAccountLimits.fulfilled, (state, action) => {
        if (state.balance) {
          state.balance.daily_limit = action.payload.daily_limit;
          state.balance.monthly_limit = action.payload.monthly_limit;
        }
      });

    // 获取余额历史
    builder
      .addCase(getBalanceHistory.fulfilled, (state, action) => {
        state.balanceHistory = action.payload.history;
      });
  },
});

export const { clearError, updateBalance, addTransaction } = accountSlice.actions;
export default accountSlice.reducer;