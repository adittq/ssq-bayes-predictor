// 格式化货币
export const formatCurrency = (amount: number): string => {
  return `¥${amount.toFixed(2)}`;
};

// 格式化数字，添加千分位分隔符
export const formatNumber = (num: number): string => {
  return num.toLocaleString('zh-CN');
};

// 格式化百分比
export const formatPercentage = (value: number, decimals: number = 2): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};

// 格式化日期
export const formatDate = (date: string | Date, format: string = 'YYYY-MM-DD'): string => {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');

  switch (format) {
    case 'YYYY-MM-DD':
      return `${year}-${month}-${day}`;
    case 'YYYY-MM-DD HH:mm':
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    case 'YYYY-MM-DD HH:mm:ss':
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    case 'MM-DD':
      return `${month}-${day}`;
    case 'HH:mm':
      return `${hours}:${minutes}`;
    default:
      return `${year}-${month}-${day}`;
  }
};

// 格式化时间差
export const formatTimeDiff = (date: string | Date): string => {
  const now = new Date();
  const target = new Date(date);
  const diff = now.getTime() - target.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) {
    return `${days}天前`;
  } else if (hours > 0) {
    return `${hours}小时前`;
  } else if (minutes > 0) {
    return `${minutes}分钟前`;
  } else {
    return '刚刚';
  }
};

// 格式化文件大小
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

// 格式化双色球号码
export const formatLotteryNumbers = (redBalls: number[], blueBall: number): string => {
  const redStr = redBalls.map(n => n.toString().padStart(2, '0')).join(' ');
  const blueStr = blueBall.toString().padStart(2, '0');
  return `${redStr} | ${blueStr}`;
};

// 格式化奖金等级
export const formatPrizeLevel = (level: number): string => {
  const levels = ['', '一等奖', '二等奖', '三等奖', '四等奖', '五等奖', '六等奖'];
  return levels[level] || '未中奖';
};

// 格式化中奖状态
export const formatWinStatus = (isWin: boolean, prizeAmount?: number): string => {
  if (!isWin) return '未中奖';
  if (prizeAmount) return `中奖 ${formatCurrency(prizeAmount)}`;
  return '中奖';
};