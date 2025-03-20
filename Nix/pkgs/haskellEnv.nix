{
  extraPackages ? [ ],
  haskellPackages,
}:
haskellPackages.ghcWithPackages (
  haskellPackages:
  with haskellPackages;
  [
    cabal-install
    fourmolu # Formatter
    stack
    # Libs
    JuicyPixels
    http-types
    warp
    mime-types
    websockets
  ]
  ++ extraPackages
)
