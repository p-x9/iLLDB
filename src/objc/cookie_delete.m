@import Foundation;

// #import <Foundation/Foundation.h>
// NSHTTPCookieStorage *storage = [NSHTTPCookieStorage sharedHTTPCookieStorage];

NSString *domain = @"<DOMAIN>";
NSString *name = @"<NAME>";
NSString *path = @"<PATH>";

NSArray *allCookies = [storage cookies];
int matchedCount = 0;

for (NSHTTPCookie *cookie in allCookies) {
  BOOL domainMatched =
      (domain == nil) || [cookie.domain isEqualToString:domain];
  BOOL nameMatched = (name == nil) || [cookie.name isEqualToString:name];
  BOOL pathMatched = (path == nil) || [cookie.path isEqualToString:path];

  if (domainMatched && nameMatched && pathMatched) {
    [storage deleteCookie:cookie];
    matchedCount++;
  }
}

if (matchedCount == 0) {
  printf("%d Cookies was deleted\n", matchedCount);
}
