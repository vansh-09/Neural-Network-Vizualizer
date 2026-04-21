#include<stdio.h>

typedef struct node
{
    int ptd, at,bt,wt,tat;
}Process;

int main()
{
    int n, i, j;
    Process p[10];
    printf("Enter the number of processes: ");
    scanf("%d", &n);
    for(i=0; i<n; i++)
    {
        printf("Enter the arrival time and burst time for process %d: ", i+1);
        scanf("%d%d", &p[i].at, &p[i].bt);
        p[i].ptd = i+1;
    }
    
    // Sort processes by arrival time
    for(i=0; i<n-1; i++)
    {
        for(j=0; j<n-i-1; j++)
        {
            if(p[j].at > p[j+1].at)
            {
                Process temp = p[j];
                p[j] = p[j+1];
                p[j+1] = temp;
            }
        }
    }
    
    // Calculate waiting time and turnaround time
    int total_wt = 0, total_tat = 0;
    for(i=0; i<n; i++)
    {
        if(i == 0)
            p[i].wt = 0;
        else
            p[i].wt = (p[i-1].at + p[i-1].bt) - p[i].at;
        
        if(p[i].wt < 0)
            p[i].wt = 0;
        
        p[i].tat = p[i].wt + p[i].bt;
        
        total_wt += p[i].wt;
        total_tat += p[i].tat;
    }
    
    // Print the results
    printf("\nProcess\tArrival Time\tBurst Time\tWaiting Time\tTurnaround Time\n");
    for(i=0; i<n; i++)
    {
        printf("%d\t%d\t\t%d\t\t%d\t\t%d\n", p[i].ptd, p[i].at, p[i].bt, p[i].wt, p[i].tat);
    }
    
    printf("\nAverage Waiting Time: %.2f\n", (float)total_wt/n);
    printf("Average Turnaround Time: %.2f\n", (float)total_tat/n);
    
    return 0;
}