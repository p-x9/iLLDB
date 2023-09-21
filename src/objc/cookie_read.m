@import Foundation;

// #import <Foundation/Foundation.h>
// NSHTTPCookieStorage *storage = [NSHTTPCookieStorage sharedHTTPCookieStorage];

NSString *domain = @"<DOMAIN>";
NSString *name = @"<NAME>";
NSString *path = @"<PATH>";

NSArray *allCookies = [storage cookies];
int matchedCount = 0;

printf("Cookie Information:\n");

for (NSHTTPCookie *cookie in allCookies) {
  BOOL domainMatched =
      (domain == nil) || [cookie.domain isEqualToString:domain];
  BOOL nameMatched = (name == nil) || [cookie.name isEqualToString:name];
  BOOL pathMatched = (path == nil) || [cookie.path isEqualToString:path];

  if (domainMatched && nameMatched && pathMatched) {
    printf("-------------------\n");

    printf("  Name:    %s\n", (char *)[cookie.name UTF8String]);
    printf("  Value:   %s\n", (char *)[cookie.value UTF8String]);
    printf("  Domain:  %s\n", (char *)[cookie.domain UTF8String]);
    printf("  Path:    %s\n", (char *)[cookie.path UTF8String]);

    NSDateFormatter *dateFormatter = [[NSDateFormatter alloc] init];
    [dateFormatter setDateFormat:@"yyyy-MM-dd HH:mm:ss"];
    NSString *formattedDate = [dateFormatter stringFromDate:cookie.expiresDate];
    printf("  Expires: %s\n", (char *)[formattedDate UTF8String]);

    printf("-------------------\n");
    matchedCount++;
  }
}

if (matchedCount == 0) {
  printf("  None\n")
}
