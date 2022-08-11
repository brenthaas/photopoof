(define (quick-print inImage)
  (let* (
         (image (car(gimp-file-load RUN-NONINTERACTIVE inImage inImage)))
         )
    (file-print-gtk RUN-INTERACTIVE image)
  )
)
