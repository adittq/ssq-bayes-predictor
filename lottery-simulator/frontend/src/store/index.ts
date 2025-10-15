import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import lotteryReducer from './slices/lotterySlice';
import accountReducer from './slices/accountSlice';
import analysisReducer from './slices/analysisSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    lottery: lotteryReducer,
    account: accountReducer,
    analysis: analysisReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;