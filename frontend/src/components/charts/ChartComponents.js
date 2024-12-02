// src/components/charts/ChartComponents.js
import React from 'react';
import {
 AreaChart, Area, BarChart, Bar, LineChart, Line,
 XAxis, YAxis, CartesianGrid, Tooltip, Legend,
 ResponsiveContainer
} from 'recharts';

const ChartContainer = ({ children }) => (
 <div style={{ width: '100%', height: '100%', minHeight: 300 }}>
   {children}
 </div>
);

export const TimePatternChart = ({ data }) => (
 <ChartContainer>
   <ResponsiveContainer>
     <AreaChart data={data || []}>
       <CartesianGrid strokeDasharray="3 3" />
       <XAxis dataKey="hour" />
       <YAxis />
       <Tooltip />
       <Legend />
       <Area 
         type="monotone" 
         dataKey="views" 
         name="조회수" 
         stroke="#8884d8" 
         fill="#8884d8" 
       />
     </AreaChart>
   </ResponsiveContainer>
 </ChartContainer>
);

export const InteractionChart = ({ data }) => (
 <ChartContainer>
   <ResponsiveContainer>
     <BarChart data={data || []}>
       <CartesianGrid strokeDasharray="3 3" />
       <XAxis dataKey="name" />
       <YAxis />
       <Tooltip />
       <Bar dataKey="value" fill="#8884d8" />
     </BarChart>
   </ResponsiveContainer>
 </ChartContainer>
);

export const RatingAnalysisChart = ({ data }) => (
 <ChartContainer>
   <ResponsiveContainer>
     <LineChart data={data || []}>
       <CartesianGrid strokeDasharray="3 3" />
       <XAxis dataKey="category" />
       <YAxis domain={[0, 5]} />
       <Tooltip />
       <Legend />
       <Line 
         type="monotone" 
         dataKey="avg_rating" 
         name="평균 평점" 
         stroke="#8884d8" 
       />
       <Line 
         type="monotone" 
         dataKey="review_count" 
         name="리뷰 수" 
         stroke="#82ca9d" 
       />
     </LineChart>
   </ResponsiveContainer>
 </ChartContainer>
);

export const PurchasePatternChart = ({ data }) => (
 <ChartContainer>
   <ResponsiveContainer>
     <BarChart data={data || []}>
       <CartesianGrid strokeDasharray="3 3" />
       <XAxis dataKey="month" />
       <YAxis />
       <Tooltip />
       <Legend />
       <Bar dataKey="amount" name="구매금액" fill="#8884d8" />
     </BarChart>
   </ResponsiveContainer>
 </ChartContainer>
);


