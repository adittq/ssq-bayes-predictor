import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { analysisAPI } from '../../services/api';

export interface Recommendation {
  red_balls: number[];
  blue_ball: number;
  confidence: number;
  analysis_type: string;
  reasoning: string;
}

export interface FrequencyData {
  number: number;
  frequency: number;
  percentage: number;
  last_appearance: string;
}

export interface TrendData {
  period: string;
  hot_numbers: number[];
  cold_numbers: number[];
  trend_score: number;
}

export interface PatternData {
  pattern_type: string;
  pattern_name: string;
  frequency: number;
  recent_occurrences: number;
  recommendation: boolean;
}

export interface AnalysisResult {
  id: number;
  name: string;
  analysis_type: string;
  parameters: Record<string, any>;
  results: Record<string, any>;
  created_at: string;
  is_favorite: boolean;
  rating: number;
}

export interface AnalysisState {
  recommendations: Recommendation[];
  frequencyAnalysis: {
    red_balls: FrequencyData[];
    blue_balls: FrequencyData[];
  } | null;
  trendAnalysis: TrendData[];
  patternAnalysis: PatternData[];
  hotColdAnalysis: {
    hot_red: number[];
    cold_red: number[];
    hot_blue: number[];
    cold_blue: number[];
  } | null;
  correlationAnalysis: {
    red_correlations: Array<{
      number1: number;
      number2: number;
      correlation: number;
    }>;
    blue_correlations: Array<{
      blue_ball: number;
      red_balls: number[];
      correlation: number;
    }>;
  } | null;
  predictionAccuracy: {
    model_name: string;
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
  }[] | null;
  modelComparison: {
    model_name: string;
    accuracy: number;
    performance_score: number;
    recommendation_quality: number;
  }[] | null;
  savedAnalyses: AnalysisResult[];
  statistics: {
    total_analyses: number;
    favorite_count: number;
    average_rating: number;
    most_used_type: string;
  } | null;
  loading: boolean;
  error: string | null;
}

const initialState: AnalysisState = {
  recommendations: [],
  frequencyAnalysis: null,
  trendAnalysis: [],
  patternAnalysis: [],
  hotColdAnalysis: null,
  correlationAnalysis: null,
  predictionAccuracy: null,
  modelComparison: null,
  savedAnalyses: [],
  statistics: null,
  loading: false,
  error: null,
};

// 获取推荐号码
export const getRecommendations = createAsyncThunk(
  'analysis/getRecommendations',
  async (params: {
    analysis_type?: string;
    period_count?: number;
  } = {}, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getRecommendations(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取推荐号码失败');
    }
  }
);

// 获取频率分析
export const getFrequencyAnalysis = createAsyncThunk(
  'analysis/getFrequencyAnalysis',
  async (params: { period_count?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getFrequencyAnalysis(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取频率分析失败');
    }
  }
);

// 获取趋势分析
export const getTrendAnalysis = createAsyncThunk(
  'analysis/getTrendAnalysis',
  async (params: { period_count?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getTrendAnalysis(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取趋势分析失败');
    }
  }
);

// 获取模式分析
export const getPatternAnalysis = createAsyncThunk(
  'analysis/getPatternAnalysis',
  async (params: { period_count?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getPatternAnalysis(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取模式分析失败');
    }
  }
);

// 获取冷热分析
export const getHotColdAnalysis = createAsyncThunk(
  'analysis/getHotColdAnalysis',
  async (params: { period_count?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getHotColdAnalysis(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取冷热分析失败');
    }
  }
);

// 获取相关性分析
export const getCorrelationAnalysis = createAsyncThunk(
  'analysis/getCorrelationAnalysis',
  async (params: { period_count?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getCorrelationAnalysis(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取相关性分析失败');
    }
  }
);

// 获取预测准确率
export const getPredictionAccuracy = createAsyncThunk(
  'analysis/getPredictionAccuracy',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getPredictionAccuracy();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取预测准确率失败');
    }
  }
);

// 获取模型比较
export const getModelComparison = createAsyncThunk(
  'analysis/getModelComparison',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getModelComparison();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取模型比较失败');
    }
  }
);

// 保存分析结果
export const saveAnalysis = createAsyncThunk(
  'analysis/saveAnalysis',
  async (data: {
    name: string;
    analysis_type: string;
    parameters: Record<string, any>;
    results: Record<string, any>;
  }, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.saveAnalysis(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '保存分析失败');
    }
  }
);

// 获取我的分析
export const getMyAnalyses = createAsyncThunk(
  'analysis/getMyAnalyses',
  async (params: { page?: number; size?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getMyAnalyses(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取我的分析失败');
    }
  }
);

// 获取分析统计
export const getAnalysisStatistics = createAsyncThunk(
  'analysis/getStatistics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analysisAPI.getAnalysisStatistics();
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取分析统计失败');
    }
  }
);

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearRecommendations: (state) => {
      state.recommendations = [];
    },
    updateAnalysisRating: (state, action: PayloadAction<{
      id: number;
      rating: number;
    }>) => {
      const analysis = state.savedAnalyses.find(a => a.id === action.payload.id);
      if (analysis) {
        analysis.rating = action.payload.rating;
      }
    },
    toggleAnalysisFavorite: (state, action: PayloadAction<number>) => {
      const analysis = state.savedAnalyses.find(a => a.id === action.payload);
      if (analysis) {
        analysis.is_favorite = !analysis.is_favorite;
      }
    },
  },
  extraReducers: (builder) => {
    // 获取推荐号码
    builder
      .addCase(getRecommendations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getRecommendations.fulfilled, (state, action) => {
        state.loading = false;
        state.recommendations = action.payload;
      })
      .addCase(getRecommendations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // 获取频率分析
    builder
      .addCase(getFrequencyAnalysis.fulfilled, (state, action) => {
        state.frequencyAnalysis = action.payload;
      });

    // 获取趋势分析
    builder
      .addCase(getTrendAnalysis.fulfilled, (state, action) => {
        state.trendAnalysis = action.payload;
      });

    // 获取模式分析
    builder
      .addCase(getPatternAnalysis.fulfilled, (state, action) => {
        state.patternAnalysis = action.payload;
      });

    // 获取冷热分析
    builder
      .addCase(getHotColdAnalysis.fulfilled, (state, action) => {
        state.hotColdAnalysis = action.payload;
      });

    // 获取相关性分析
    builder
      .addCase(getCorrelationAnalysis.fulfilled, (state, action) => {
        state.correlationAnalysis = action.payload;
      });

    // 获取预测准确率
    builder
      .addCase(getPredictionAccuracy.fulfilled, (state, action) => {
        state.predictionAccuracy = action.payload;
      });

    // 获取模型比较
    builder
      .addCase(getModelComparison.fulfilled, (state, action) => {
        state.modelComparison = action.payload;
      });

    // 保存分析结果
    builder
      .addCase(saveAnalysis.fulfilled, (state, action) => {
        state.savedAnalyses.unshift(action.payload);
      });

    // 获取我的分析
    builder
      .addCase(getMyAnalyses.fulfilled, (state, action) => {
        state.savedAnalyses = action.payload.analyses;
      });

    // 获取分析统计
    builder
      .addCase(getAnalysisStatistics.fulfilled, (state, action) => {
        state.statistics = action.payload;
      });
  },
});

export const {
  clearError,
  clearRecommendations,
  updateAnalysisRating,
  toggleAnalysisFavorite,
} = analysisSlice.actions;
export default analysisSlice.reducer;